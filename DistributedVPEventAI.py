from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI


class DistributedVPEventAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedVPEventAI')

    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)

        self.active = False

    def setActive(self, state):
        self.active = state

    def vpDestroyed(self):
        if self.active:
            return

        self.active = True

        self.sendUpdate('vpDestroyed', [])

        taskMgr.doMethodLater(10.0, self.setActive, self.uniqueName('vpDestroyed'), extraArgs=[False])
