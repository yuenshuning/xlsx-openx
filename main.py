import xlrd3 as xlrd
import codecs,re, os
from lxml import etree
from copy import deepcopy

SOURCE_FILE = "./0708.xlsx"
TEMPLATE_XODR_FILE = "./template/template.xodr"
TEMPLATE_XOSC_FILE = "./template/template.xosc"
START_ROW = 5   # 约定场景描述从第5行开始

def removeSuffix(path):
    pos_end = path.rfind(".")
    pos_start = path.rfind("/")
    return path[pos_start+1 : pos_end]

# 直道
def createLine(road):
    # 约定road_sheet的第B-N列为描述直道
    # 道路长度 1列
    road.set('length', str(road_data[1].value))
    plan_view = road.find('planView')
    geometry = plan_view.find('geometry')       
    geometry.set('length', str(road_data[1].value))
    # 几何形状
    etree.SubElement(geometry, 'line')
    # 道路坡度 2列
    elevation_profile = road.find('elevationProfile')
    elevation = elevation_profile.find('elevation')
    elevation.set('b', str(road_data[2].value/road_data[1].value))
    # 道路倾斜度 3列
    lateral_profile = road.find('lateralProfile')
    superelevation = lateral_profile.find('superelevation')
    superelevation.set('a', str(road_data[3].value))
    # 路面质量

    lane_section = road.find('lanes').find('laneSection')
    # 正向车道 6列       
    right_lanes = lane_section.find('right')
    right_lane_template = right_lanes.find('lane')
    for i in range(int(road_data[6].value)):
        # lane_id默认从-1递减
        lane_id = - (i + 1)
        if lane_id < -1:
            right_lane_template = deepcopy(right_lane_template)
            right_lanes.append(right_lane_template)
        right_lane_template.set('id', str(lane_id))
        # 车道宽度 8列
        right_lane_width = right_lane_template.find('width')
        right_lane_width.set('a', str(road_data[8].value))
        # 车道线类型及颜色 9列10列
        road_mark_type = re.sub('\[|\'|\]|\s*','',road_data[9].value)
        road_mark_type = road_mark_type.split(',')
        road_mark_color = re.sub('\[|\'|\]|\s*','',road_data[10].value)
        road_mark_color = road_mark_color.split(',')

        right_lane_mark = right_lane_template.find('roadMark')
        right_lane_mark.set('type', road_mark_type[2])
        right_lane_mark.set('color', road_mark_color[2])
        # 路面附着系数 4列
        right_lane_material = right_lane_template.find('material')
        right_lane_material.set('friction', str(road_data[4].value))
    
    # 反向车道 7列
    left_lanes = lane_section.find('left')
    left_lane_template = left_lanes.find('lane')
    for i in range(int(road_data[7].value)):
        # lane_id默认从1递增
        lane_id = i + 1
        if lane_id > 1:
            left_lane_template = deepcopy(left_lane_template)
            left_lanes.append(left_lane_template)
        left_lane_template.set('id', str(lane_id))
        # 车道宽度 8列
        left_lane_width = left_lane_template.find('width')
        left_lane_width.set('a', str(road_data[8].value))
        # 车道线类型及颜色 9列10列
        road_mark_type = re.sub('\[|\'|\]|\s*', '', road_data[9].value)
        road_mark_type = road_mark_type.split(',')
        road_mark_color = re.sub('\[|\'|\]|\s*', '', road_data[10].value)
        road_mark_color = road_mark_color.split(',')

        left_lane_mark = left_lane_template.find('roadMark')
        left_lane_mark.set('type', str(road_mark_type[2]))
        left_lane_mark.set('color', str(road_mark_color[2]))
        # 路面附着系数 4列
        left_lane_material = left_lane_template.find('material')
        left_lane_material.set('friction', str(road_data[4].value))

def createAcr(road):
    pass

def importXlsx(path):
    data = xlrd.open_workbook(path, encoding_override="utf-8")
    base = data.sheet_by_name("具体场景描述")
    open_drive = data.sheet_by_name("具体场景-道路类型参数库")
    return base, open_drive

def exportXodr(base_xodr, path):
    f = codecs.open(path, 'w','utf-8')
    f.write(etree.tounicode(base_xodr))
    f.close()
	
def extendXodr(base_xodr, base_data, road_data):
    # 约定base_sheet的第D-H列为道路类型
    road_type = 3
    for col in range(3,8):
        if base_data[col].value == 1:
            road_type = col

    root = base_xodr.getroot()
    road = root.find('road')

    if road_type == 3:
        # 直道
        createLine(road)       
    elif road_type == 4:
        # 弯道
        createAcr(road)
    elif road_type == 5:
        # 道路变化
        # TODO
        pass
    elif road_type == 6:
        # 十字路口
        # TODO
        pass
    elif road_type == 7:
        # 匝道
        # TODO
        pass

    # 静态物体
    road_objects = road.find('objects')
    road_object = etree.Element('object')
    # 静态物体类型 8列I
    road_object.set('type', str(base_data[8].value))
    # 静态物体位置 9列J
    road_object_pos = re.sub('\[|\]|\s*', '', base_data[9].value)
    road_object_pos = road_object_pos.split(',')
    road_object.set('s', str(road_object_pos[0]))
    road_object.set('t', str(road_object_pos[1]))
    road_objects.append(road_object)
    # 护栏
    road_object = etree.Element('object')
    # 护栏位置 10列
    road_object_pos = re.sub('\[|\]|\s*', '', base_data[10].value)
    road_object_pos = road_object_pos.split(',')
    road_object.set('s', str(road_object_pos[0]))
    road_object.set('t', str(road_object_pos[1]))
    road_objects.append(road_object)
    # 交通标识牌
    road_object = etree.Element('object')
    # 交通标识牌类型 11列
    road_object.set('type', str(base_data[11].value))
    # 交通标识牌位置 12列
    road_object_pos = re.sub('\[|\]|\s*', '', base_data[12].value)
    road_object_pos = road_object_pos.split(',')
    road_object.set('s', str(road_object_pos[0]))
    road_object.set('t', str(road_object_pos[1]))
    road_objects.append(road_object)
    # 交通信号灯
    road_signals = road.find('signals')
    road_signal = etree.Element('signal')
    # 交通信号灯类型 13列
    road_signal_type = re.sub('\[|\]|\s*', '', base_data[13].value)
    road_signal_type = road_signal_type.split(',')
    road_signal.set('type', str(road_signal_type[0]))
    road_signal.set('subtype', str(road_signal_type[1]))
    # 交通标识牌位置 14列
    road_signal_pos = re.sub('\[|\]|\s*', '', base_data[14].value)
    road_signal_pos = road_signal_pos.split(',')
    road_signal.set('s', str(road_signal_pos[0]))
    road_signal.set('t', str(road_signal_pos[1]))
    road_signals.append(road_signal)

def exportXosc(base_xosc, path):
    f = codecs.open(path, 'w','utf-8')
    f.write(etree.tounicode(base_xosc))
    f.close()
	
def extendXosc(base_xosc, base_data, road_file_path):
    root = base_xosc.getroot()
    road = root.find('RoadNetwork').find('LogicFile')
    road.set('filepath', road_file_path)
    private_actions = root.find('Storyboard').find('Init').find('Actions').findall('Private')
    # 主车
    ego_action = private_actions[0]
    ego_private_actions = ego_action.findall('PrivateAction')  
    # 主车触发时刻纵向位置16列&横向位置17列&朝向18列
    ego_tel_action = ego_private_actions[1].find('TeleportAction')
    ego_tel_action.find('Position').find('LanePosition').set('s', str(base_data[16].value))
    ego_tel_action.find('Position').find('LanePosition').set('laneId', str(base_data[17].value))
    ego_tel_action.find('Position').find('LanePosition').find('Orientation').set('h', str(base_data[18].value))
    # 主车触发时刻纵向速度19列
    ego_longi_action = ego_private_actions[0].find('LongitudinalAction')
    ego_longi_action.find('SpeedAction').find('SpeedActionTarget').find('AbsoluteTargetSpeed').set('value', str(base_data[19].value))
    # 目标车
    vut_action = private_actions[1]
    vut_private_actions = vut_action.findall('PrivateAction')
    # 目标车类型22列
    root.find('Entities').findall('ScenarioObject')[1].find('CatalogReference').set('entryName', str(base_data[22].value))
    # 目标车触发时刻纵向位置23列&横向位置24列&航向角25列
    vut_tel_action = vut_private_actions[1].find('TeleportAction')
    vut_tel_action.find('Position').find('RelativeRoadPosition').set('ds', str(base_data[23].value))
    vut_tel_action.find('Position').find('RelativeRoadPosition').set('dt', str(base_data[24].value))
    vut_tel_action.find('Position').find('RelativeRoadPosition').find('Orientation').set('h', str(base_data[25].value))
    # 目标车触发时刻纵向速度26列
    vut_longi_action = vut_private_actions[0].find('LongitudinalAction')
    vut_longi_action.find('SpeedAction').find('SpeedActionTarget').find('AbsoluteTargetSpeed').set('value', str(base_data[26].value))
    # 横向动作类型30列
    private_actions = root.find('Storyboard').find('Story').find('Act').find('ManeuverGroup').find(
        'Maneuver').find('Event').find('Action').find('PrivateAction').find('LateralAction').find(
        'LaneChangeAction').find('LaneChangeActionDynamics').set('dynamicsShape', str(base_data[30].value))
    private_actions = root.find('Storyboard').find('Story').find('Act').find('ManeuverGroup').find(
        'Maneuver').find('Event').find('Action').find('PrivateAction').find('LateralAction').find(
        'LaneChangeAction').find('LaneChangeActionDynamics').set('value', '3')
    # 动作持续时间31列
    action_dur = re.sub('\[|\]|\s*', '', base_data[31].value)
    action_dur = action_dur.split(',')
    private_actions = root.find('Storyboard').find('Story').find('Act').find('ManeuverGroup').find(
        'Maneuver').find('Event').find('StartTrigger').find('ConditionGroup').find('Condition').find(
        'ByValueCondition').find('SimulationTimeCondition').set('value', str(action_dur[0]))
    private_actions = root.find('Storyboard').find('StopTrigger').find('ConditionGroup').find('Condition').find(
        'ByValueCondition').find('SimulationTimeCondition').set('value', str(action_dur[1]))

if __name__ == "__main__": 
    # 打开场景描述excel
    base_sheet, road_sheet = importXlsx(SOURCE_FILE)
    # 取每个子表行数的最小值
    min_row_length = min(base_sheet.nrows, road_sheet.nrows)
    # 约定场景描述从第5行开始，遍历每个场景描述
    for num in range(START_ROW - 1, min_row_length):
        base_data = base_sheet.row(num)
        road_data = road_sheet.row(num)
        scenario_id = base_data[0].value      # 约定每行的第一列为场景编号
        # 约定输出的文件名为 SOURCE_FILE-场景编号
        target_file_name = '{}-{}'.format(removeSuffix(SOURCE_FILE), scenario_id)
        dir_path = os.path.abspath(os.path.dirname(__file__))
        target_xodr_path = '{}/xodr/{}.xodr'.format(dir_path, target_file_name)
        target_xosc_path = '{}/xosc/{}.xosc'.format(dir_path, target_file_name)

        # 基于xodr模板，按照excel描述，插入节点
        base_xodr = etree.parse(TEMPLATE_XODR_FILE)        
        extendXodr(base_xodr, base_data, road_data)
        # 导出xodr文件
        exportXodr(base_xodr, target_xodr_path)
        
        # 基于xodr模板，按照excel描述，插入节点
        base_xosc = etree.parse(TEMPLATE_XOSC_FILE)
        extendXosc(base_xosc, base_data, os.path.abspath(target_xodr_path))
        # 导出xodr文件
        exportXosc(base_xosc, target_xosc_path)