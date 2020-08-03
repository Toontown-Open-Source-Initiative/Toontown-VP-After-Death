from direct.interval.IntervalGlobal import *
from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObject import DistributedObject

from panda3d.core import *

from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from toontown.battle import MovieUtil
from toontown.distributed import DelayDelete
from toontown.suit import BossCog
from toontown.suit import SuitDNA


class DistributedVPEvent(DistributedObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedCogKart')

    def __init__(self, cr):
        DistributedObject.__init__(self, cr)
        self.activeIntervals = {}
        self.boss = None
        self.fallingSfx = None
        self.impactSfx = None

    def announceGenerate(self):
        DistributedObject.announceGenerate(self)

        # Make our boss
        self.boss = BossCog.BossCog()

        # Create out DNA and assign it the Boss
        dna = SuitDNA.SuitDNA()
        dna.newBossCog('s')
        self.boss.setDNA(dna)

        # Add him properly and activate shadow
        self.boss.addActive()
        self.boss.initializeDropShadow()

        # Position and hide him
        self.boss.setPos(0.90, -190.16, 268.0)
        self.boss.setHpr(0.0, 0.0, 26.0)
        self.boss.setColorScale(1.0, 1.0, 1.0, 0.0)
        self.boss.setTransparency(1)
        self.boss.reparentTo(render)
        self.boss.pingpong('Bb2Ff_spin', fromFrame=1, toFrame=30)
        self.boss.hide()

        self.fallingSfx = loader.loadSfx('phase_9/audio/sfx/CHQ_VP_big_death.ogg')
        self.impactSfx = loader.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart.ogg')

    def delete(self):
        DistributedObject.delete(self)

        self.cleanupIntervals()

    def storeInterval(self, interval, name):
        if name in self.activeIntervals:
            ival = self.activeIntervals[name]
            if hasattr(ival, 'delayDelete') or hasattr(ival, 'delayDeletes'):
                self.clearInterval(name, finish=1)
        self.activeIntervals[name] = interval

    def cleanupIntervals(self):
        for interval in list(self.activeIntervals.values()):
            interval.finish()
            DelayDelete.cleanupDelayDeletes(interval)

        self.activeIntervals = {}

    def clearInterval(self, name, finish = 1):
        if name in self.activeIntervals:
            ival = self.activeIntervals[name]
            if finish:
                ival.finish()
            else:
                ival.pause()
            if name in self.activeIntervals:
                DelayDelete.cleanupDelayDeletes(ival)
                del self.activeIntervals[name]
        else:
            self.notify.debug('interval: %s already cleared' % name)

    def finishInterval(self, name):
        if name in self.activeIntervals:
            interval = self.activeIntervals[name]
            interval.finish()

    def resetVp(self):
        self.boss.hide()
        self.boss.setPos(0.90, -190.16, 268.0)
        self.boss.setColorScale(1.0, 1.0, 1.0, 0.0)
        self.boss.setScale(1)

        self.boss.setDizzy(False)

    def vpDestroyed(self):
        ivalName = self.uniqueName('vpDestroyed')
        self.cleanupIntervals()

        endPos = (0.90, -190.16, -20.0)
        ival = Sequence(Wait(1.5), Func(self.boss.show), Func(base.playSfx, self.fallingSfx),
                        Parallel(LerpColorScaleInterval(self.boss, 3.5, (1.0, 1.0, 1.0, 1.0)),
                                 LerpHprInterval(self.boss, 6.0, (0.0, 720.0, 26.0)),
                                 LerpPosInterval(self.boss, 6.0, endPos, blendType='easeIn')),
                        Func(base.playSfx, self.impactSfx), Func(self.boss.setDizzy, True),
                        Func(self.boss.setHpr, 33.0, -16.0, 26.0), MovieUtil.createKapowExplosionTrack(self.boss, scale=15.0),
                        Wait(2.5), LerpScaleInterval(self.boss, 1.0, (0.001, 0.001, 0.001)),
                        Func(self.resetVp))

        self.storeInterval(ival, ivalName)
        ival.start()
