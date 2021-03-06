from Annotator.frame import Frame
import copy


class Instance(object):

    def __init__(self, id, index, color, name, ccolor, cname):
        self.id = id
        self.color = color
        self.name = name
        self.customColor = ccolor
        self.customName = cname
        self.index = index
        self.boxes = {}  # { framenum: box }
        self.maxFrame = 0

    def updateBoxes(self, box, frame, conf=-1):
        b = self.cleanBox(box)
        b['conf'] = conf
        self.boxes[frame.frameNum] = b
        if frame.frameNum > self.maxFrame:
            self.maxFrame = frame.frameNum
        frame.addInstance(self.id, b)

    def updateId(self, newId, frameNum, oldFrames):
        newFrames = oldFrames
        for key in self.boxes:
            if int(key) >= frameNum:
                workingFrame = oldFrames[int(key)]  # frame
                workingFrame.instances[newId] = self.boxes[key]
                workingFrame.instances.pop(self.id)
                newFrames[int(key)] = workingFrame
        return newFrames

    def swapId(self, second, frameNum, frames, idsHaveChanged):
        # frame will store all instances on it in a dictionary { instance: box }
        a = self
        b = second
        laterTrack = b
        if a.maxFrame >= b.maxFrame:
            laterTrack = a

        idsHaveChanged.append(a)
        idsHaveChanged.append(b)

        keys = copy.deepcopy(list(laterTrack.boxes.keys()))
        for key in keys:
            key = int(key)
            if key >= frameNum:
                a_short = a.boxes.get(key)
                b_short = b.boxes.get(key)
                a_long = frames[key].instances.get(a.id)
                b_long = frames[key].instances.get(b.id)

                aIsNone, bIsNone = True, True
                if a_short is not None:
                    a_short['color'] = str(b.color)
                    a_long['color'] = str(b.color)
                    aIsNone = False
                if b_short is not None:
                    b_short['color'] = str(a.color)
                    b_long['color'] = str(a.color)
                    bIsNone = False

                a.boxes[key], b.boxes[key] = b_short, a_short
                frames[key].instances[a.id], frames[key].instances[b.id] = b_long, a_long

                if aIsNone:
                    b.boxes.pop(key)
                    frames[key].instances.pop(b.id)
                    a_short = False
                if bIsNone:
                    a.boxes.pop(key)
                    frames[key].instances.pop(a.id)
                    b_short = False

        a.maxFrame, b.maxFrame = b.maxFrame, a.maxFrame

    def mergeId(self, second, frameNum, frames, idsHaveChanged):
        # frame will store all instances on it in a dictionary { instance: box }
        a = self
        b = second
        tempmax = -1

        idsHaveChanged.append(a)
        idsHaveChanged.append(b)

        keys = copy.deepcopy(list(a.boxes.keys()))
        for key in keys:
            key = int(key)
            a_short = a.boxes.get(key)
            b_short = b.boxes.get(key)
            a_long = frames[key].instances.get(a.id)

            if b_short is None:
                a_short['color'] = str(b.color)
                a_long['color'] = str(b.color)

                b.boxes[key] = a_short
                frames[key].instances[b.id] = a_long

                a.boxes.pop(key)
                frames[key].instances.pop(a.id)
            else:
                if key > tempmax:
                    tempmax = key

        a.maxFrame = tempmax

    def uniteId(self, second, frameNum, frames, idsHaveChanged):
            # frame will store all instances on it in a dictionary { instance: box }
            a = self
            b = second
            tempmax = -1

            idsHaveChanged.append(a)
            idsHaveChanged.append(b)

            keys = copy.deepcopy(list(a.boxes.keys()))
            for key in keys:
                key = int(key)
                a_short = a.boxes.get(key)
                b_short = b.boxes.get(key)
                a_long = frames[key].instances.get(a.id)

                if b_short is None:
                    a_short['color'] = str(b.color)
                    a_long['color'] = str(b.color)

                    b.boxes[key] = a_short
                    frames[key].instances[b.id] = a_long
                else:
                    x1 = min(a_short['x1'], b_short['x1'])
                    x2 = max(a_short['x2'], b_short['x2'])
                    y1 = min(a_short['y1'], b_short['y1'])
                    y2 = max(a_short['y2'], b_short['y2'])

                    b.boxes[key] = {"x1": x1, "y1": y1, "x2": x2, "y2": y2, "color": b.color}
                    frames[key].instances[b.id] = b.boxes[key]

                a.boxes.pop(key)
                frames[key].instances.pop(a.id)

    def deleteId(self, frames):
        for key in self.boxes:
            if frames[key].instances.get(self.id) is not None:
                frames[key].instances.pop(self.id)
        self.boxes = {}

    def cleanBox(self, box):
        # box = { x1, y1, x2, y2, color }
        # make the box go from top left to bottom right
        if box['x1'] > box['x2']:
            newx1, newx2 = box['x2'], box['x1']
        else:
            newx1, newx2 = box['x1'], box['x2']
        if box['y1'] > box['y2']:
            newy1, newy2 = box['y2'], box['y1']
        else:
            newy1, newy2 = box['y1'], box['y2']

        return {"x1": newx1, "y1": newy1, "x2": newx2, "y2": newy2, "color": self.color}
