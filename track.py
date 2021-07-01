from scipy.spatial import distance as dist
from collections import OrderedDict
import numpy as np
class CentroidTracker():
    def __init__(self, maxDisappeared=1000):
        # 下一个目标的ID。
        self.nextObjectID = 0
        # 存储ID：中心点的字典。
        self.objects = OrderedDict()
        # 存储ID，目标消失帧数的字典。
        self.disappeared = OrderedDict()
        # 目标被认为消失所消失的连续帧数。
        self.maxDisappeared = maxDisappeared
    
    def register(self, centroid, rect):
        # 当注册目标时，ID：centorid
        self.objects[self.nextObjectID] = [centroid, rect]
        self.disappeared[self.nextObjectID] = 0
        self.nextObjectID += 1

    def deregister(self, objectID):
        # 注销目标，删除ID，并在disappeared列表中将其删除。
        del self.objects[objectID]
        del self.disappeared[objectID]

    def update(self, input_rects):
        '''
            输入当前帧所有检测到的box。
        '''
		# 当前帧检测到的目标（box）数量为空时。
        if len(input_rects) == 0:
			# 遍历当前所有记录消失的ID：增加其消失数量，同时注销消失过久的ID。
            for objectID in list(self.disappeared.keys()):
                self.disappeared[objectID] += 1
                # 如果某ID消失的帧数大于阈值，则注销该ID。
                if self.disappeared[objectID] > self.maxDisappeared:
                    self.deregister(objectID)
            # （提前返回），返回当前跟踪的目标。
            return self.objects

        # 根据输入rects计算得到其对应的中心点inputCentroids
        inputCentroids = np.zeros((len(input_rects), 2), dtype="int")
        for (i, (startX, startY, endX, endY)) in enumerate(input_rects):
            # use the bounding box coordinates to derive the centroid
            cX = int((startX + endX) / 2.0)
            cY = int((startY + endY) / 2.0)
            inputCentroids[i] = (cX, cY)
            
        # 如果当前没有跟踪任务目标，则注册当前帧检测到的目标。
        if len(self.objects) == 0:
            for i in range(0, len(inputCentroids)):
                self.register(inputCentroids[i], input_rects[i])
        # 如果当前正在跟踪目标，则对比已跟踪目标中心点和当前帧目标的中心点，寻找对应关系。
        else:
            # 提取当前跟踪目标的ID及中心点
            objectIDs = list(self.objects.keys())
            objectCentroids = [i[0] for i in list(self.objects.values())]
            # 计算已跟踪目标的中心点及当前输入目标的中心点之间的距离
            D = dist.cdist(np.array(objectCentroids), inputCentroids)
            # 寻找距离矩阵中每一行的最小值，并对最小值进行排序，得到排序后的行索引值。
            # rows为，每行最小值相对大小的索引值，其中rows[0]=N，N为逐行最小值中最小值所在行号。
            rows = D.min(axis=1).argsort()
            # 逐行最小值所在列号，按照rows对应行号排序后的结果。
            cols = D.argmin(axis=1)[rows]
            # in order to determine if we need to update, register,
            # or deregister an object we need to keep track of which
            # of the rows and column indexes we have already examined
            usedRows = set()
            usedCols = set()
            # 从最佳匹配开始遍历所有匹配结果。
            for (row, col) in zip(rows, cols):
                if row in usedRows or col in usedCols:
                    continue
                # 第row个目标的ID和第col个中心点匹配。
                # 过程：1. 取第row个目标的ID，
                #      2. 将第col个中心点赋值给1得到ID的目标值。
                #      3. 第row个目标ID没有消失。
                objectID = objectIDs[row]
                self.objects[objectID] = [inputCentroids[col],input_rects[col]]
                self.disappeared[objectID] = 0
                # indicate that we have examined each of the row and
                # column indexes, respectively
                usedRows.add(row)
                usedCols.add(col)
            # 检查没有用到的行和列，即为丢失或新增的。
            unusedRows = set(range(0, D.shape[0])).difference(usedRows)
            unusedCols = set(range(0, D.shape[1])).difference(usedCols)
            # 当前跟踪的中心点个数（目标数）大于等于输入的中心点个数时，需要检查是否有目标消失。
            # 行数大于等于列数，表示当前中心点数大于输入中心点数
            if D.shape[0] >= D.shape[1]:
                # loop over the unused row indexes
                # 遍历没有匹配的行
                for row in unusedRows:
                    # 提取改行对应的目标ID，将其消失的次数+1
                    objectID = objectIDs[row]
                    self.disappeared[objectID] += 1
                    # 检查该目标是否在连续帧中多次未出现，若是，则注销之
                    if self.disappeared[objectID] > self.maxDisappeared:
                        self.deregister(objectID)
            # 输入帧目标个数大于当前跟踪目标个数，则注册新目标。
            else:
                for col in unusedCols:
                    self.register(inputCentroids[col],input_rects[col])
        # return the set of trackable objects
        return self.objects
    
    
def get_object_label(objects, rects):
    '''
        从跟踪的objects获取输入rect的label
    '''
    labels = []
    for rect in rects:
        for k, v in objects.items():
            if rect in v:
                labels.append(k)
                break
    return labels