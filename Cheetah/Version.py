Version = '3.0.0a1'
VersionTuple = (3, 0, 0, 'alpha', 1)

MinCompatibleVersion = '3.0.0a1'
MinCompatibleVersionTuple = (3, 0, 0, 'alpha', 1)

####
def convertVersionStringToTuple(s):
    versionNum = [0, 0, 0]
    releaseType = 'final'
    releaseTypeSubNum = 0
    if s.find('a')!=-1:
        num, releaseTypeSubNum = s.split('a')
        releaseType = 'alpha'
    elif s.find('b')!=-1:
        num, releaseTypeSubNum = s.split('b')
        releaseType = 'beta'
    elif s.find('rc')!=-1:
        num, releaseTypeSubNum = s.split('rc')
        releaseType = 'candidate'
    else:
        num = s
    num = num.split('.')
    for i in range(len(num)):
        versionNum[i] = int(num[i])
    if len(versionNum)<3:
        versionNum += [0]
    releaseTypeSubNum = int(releaseTypeSubNum)

    return tuple(versionNum+[releaseType, releaseTypeSubNum])
