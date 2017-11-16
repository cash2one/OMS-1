
class CustomException(Exception):
    ''' 自定义异常 '''
    pass


class CopException(Exception):
    ''' Cop异常 '''
    pass


class PingppException(Exception):
    ''' Ping++异常 '''
    pass


def is_not_exist(error):
    ''' 资源不存在 '''
    return error[0] > 10000 and error[0] < 12000


def is_already_exist(error):
    ''' 资源已存在 '''
    return error[0] > 12000 and error[0] < 14000


def is_parameter_invalid(error):
    ''' 参数错误 '''
    return error[0] > 14000 and error[0] < 16000


def is_operate_failed(error):
    ''' 操作失败 '''
    return error[0] > 16000 and error[0] < 18000


def is_oauth_failed(error):
    ''' 授权失败 '''
    return error[0] > 20000 and error[0] < 22000


def is_server_error(error):
    ''' 服务器异常 '''
    return error[0] > 22000 and error[0] < 24000


''' 前端展示(10001~20000)'''
# 资源没有找到类(10001~11999)
PRODUCT_NOT_EXIST = (10001, "商品没有找到")
USER_NOT_EXIST = (10002, "用户没有找到")
COMPANY_INFO_NOT_FOUND = (10003, "公司资料没有找到")
WAREHOUSE_NOT_FOUND = (10004,  "仓库没有找到")
WAREHOUSE_CHOICE_NOT_FOUND = (10005, "分仓申请没有找到")
WAREHOUSE_SERVICE_NOT_FOUND = (10006, "仓库服务没有找到")
SKU_CATEGORY_NOT_FOUND = (10007, "仓库没有找到")
SKU_WAREHOUSE_NOT_FOUND = (10008, "库存没有找到")
ORDER_NOT_FOUND = (10009, "订单没有找到")
ORDER_DETAIL_NOT_FOUND = (10010, "订单详情没有找到")
ACTIVITY_NOT_FOUND = (10011, "活动没有找到")
PLATFORM_NOT_FOUND = (10012, "平台没有找到")
STOCK_IN_NOT_FOUND = (10013, "入库单没有找到")
STOCK_IN_DETAIL_NOT_FOUND = (10014, "入库单详情没有找到")
STOCK_TRANSFER_NOT_FOUND = (10015, "调拨单没有找到")
STORE_NOT_FOUND = (10016, "店铺没有找到")
DEVELOPE_ACCOUNT_NOT_FOUND = (10017, "开发者帐号没有找到")
ACCORD_NOT_FOUND = (11998, "记录没有找到")
RESOURCE_NOT_FOUND = (11999, "资源没有找到")

# 资源已存在(12001~13999)
PHONE_IS_ALREADY_REGISTER = (14002, "该手机号码已注册")
ALREADY_FAVORITE_THIS_WAREHOUSE = (14003, "已收藏该仓库")
ACCOUNT_IS_EXIST = (14004, "账号已存在")


# 参数错误(14001~15999)
PARAMETER_MISSING = (14001, "参数缺失")
WRONG_PHONE = (14002, "手机号码错误")
USER_OR_PASSWORD_IS_INVALID = (14003, "用户名或密码错误")
AMOUNT_IS_INCORRECT = (14004, "金额不正确")
OVERDUE_AMOUNT_IS_ZERO = (14005, "逾期费为0")
NOT_SUPPORTED_BILL_TYPE = (14006, "不支持的账单类别")
NOT_SUPPORTED_RECEIPT_TYPE = (14007, "不支持的收入类别")
WITHDRAW_AMOUNT_MORE_THAN_BALANCE = (14007, "提现金额大于余额")
STORE_KEY_IS_REQURIED = (14008, "需要store key参数")


# 操作失败(16001~17999)
LOGIN_FAILURE = (16001, "用户登录失败")
UPDATE_PHONE_FAILURE = (16002, "手机修改失败")
SMS_CODE_IS_INVALID = (16003, "验证码校验失败")
GET_SMS_CODE_FAILURE = (16004, "获取验证码失败")
GET_OAUTH_RIGHT_FAILUE = (16005, "获取授权失败")
UPDATE_PASSWORD_FAILURE = (16006, "密码修改失败")
GET_SMS_CODE_FREQUENTLY = (16007, "获取验证码频繁")
PLEASE_INVALID_OLD_PHONE = (16008, "请校验旧手机号码")
USER_IS_ALREADY_BIND_PHONE = (16009, "用户已经绑定手机")
USER_IS_ALREADY_BIND_PHONE = (16010, "用户已经绑定用户")
UNSOUPPORT_LOGIN_METHOD = (16011, "不支持的登录方式")
USER_ADD_FAILURE = (16012, "用户新增失败")
WAREHOUSE_CREATE_FAILURE = (16013, "仓库创建失败")
WAREHOUSE_CHOICE_FAILURE = (16014, "分仓申请失败")
WAREHOUSE_REPORT_FAILURE = (16015, "分仓报告失败")
POSITION_LIST_ERROR = (16016, "获取职能列表失败")
FUNCTION_LIST_ERROR = (16017, "获取功能列表失败")
DEPARTMENT_LIST_ERROR = (16018, "获取部门列表失败")
POSITION_FUNCTION_LIST_ERROR = (16019, "获取职能功能列表失败")
DEPARTMENT_FUNCTION_LIST_ERROR = (16020, "获取部门功能列表失败")
SYNC_SINGLEITEM_FAILURE = (16021, "同步商品失败")
SYNC_ENTRYORDER_FAILUE = (16022, "同步入库单失败")
ORDER_IS_ALREADY_CHECKD = (16023, "订单已审核")
ORDER_IS_LOCKED = (16024, "订单已锁定")
INVALID_ADDRESS = (16025, "地址非法")
INVENTORY_LACKING = (16026, "库存不足")

''' 分割线前端不需要展示 '''
# 授权失败(20001~21999)
TOKEN_EXPIRE = (20001, "token过期")
TOKEN_INVALID = (20002, "token非法")
TOKEN_NOT_EXIST = (20003, "token不存在")
AUTH_FAILURE = (20004, "授权失败")

# 服务器错误(22001~23999)
SERVER_ERROR = (22001, "服务器异常")
BAIDU_API_GET_COOR_FAILURE = (22002, "百度API获取经纬度失败")
BAIDU_API_GET_DISTANCE_FAILURE = (22003, "百度API获取距离失败")
EXPRESS_PRICE_SHEET_NOT_FOUND = (22004, "快递价格表没有找到")
STORGE_PRICE_SHEET_NOT_FOUND = (22005, "仓储价格表没有找到")
PINGPP_CALLBACK_FAILURE = (22006, "ping++回调失败")


# PRODUCT_NOT_EXIST = (10001, "商品不存在")
# USER_NOT_EXIST = (10013, "用户不存在")
# PARAMETER_MISSING = (13000, "参数缺失")
# WRONG_PHONE = (13001, "手机号码错误")
# SMS_CODE_IS_INVALID = (14001, "验证码校验失败")
# PHONE_IS_ALREADY_REGISTER = (14002, "该手机号码已注册")
# USER_CREATE_FAILURE = (14003, "用户创建失败")
# GET_SMS_CODE_FAILUE = (14003, "获取验证码失败")
# GET_SMS_CODE_FREQUENTLY = (14004, "获取验证码频繁")
# SMS_CODE_INVALID = (14005, "验证码校验失败")
# UNSOUPPORT_LOGIN_METHOD = (14006, "不支持的登录方式")
# USER_OR_PASSWORD_IS_INVALID = (14008, "用户名或密码错误")
# LOGIN_FAILURE = (14009, "用户登录失败")
# GET_OAUTH_RIGHT_FAILUE = (14010, "获取授权失败")
# USER_IS_ALREADY_BIND_PHONE = (14011, "用户已经绑定用户")
# PLEASE_INVALID_OLD_PHONE = (14012, "请校验旧手机号码")
# UPDATE_PHONE_FAILURE = (14013, "手机修改失败")
# UPDATE_PASSWORD_FAILURE = (14014, "密码修改失败")
# WAREHOUSE_CREATE_FAILURE = (15001, "仓库创建失败")
# WAREHOUSE_CHOICE_FAILURE = (15002, "分仓申请失败")
# WAREHOUSE_REPORT_FAILURE = (15005, "分仓报告失败")
# ALREADY_FAVORITE_THIS_WAREHOUSE = (15003, "已收藏该仓库")
# WAREHOUSE_APPROVE_FAILURE = (15004, "获取分仓申请列表失败")
# COMPANY_INFO_NOT_FOUND = (15006, "公司资料没有找到")
# WAREHOUSE_NOT_FOUND = (15010,  "仓库不存在")
# WAREHOUSE_CHOICE_NOT_FOUND = (15012, "分仓申请不存")
# FUNCTION_LIST_ERROR = (16001, "获取功能列表失败")
# DEPARTMENT_LIST_ERROR = (16002, "获取部门列表失败")
# DEPARTMENT_FUNCTION_LIST_ERROR = (16003, "获取部门功能列表失败")
# POSITION_LIST_ERROR = (16004, "获取职能列表失败")
# POSITION_FUNCTION_LIST_ERROR = (16005, "获取职能功能列表失败")
# USER_ADD_FAILURE = (16006, "用户新增失败")
# ACCOUNT_IS_EXIST = (16007, "账号已存在")
# WAREHOUSE_SERVICE_NOT_FOUND = (17010, "仓库服务不存在")


# ERRORS = [
#     {"code": ERROR_CODE.PRODUCT_NOT_EXIST, "message": "商品不存在"},
#     {"code": ERROR_CODE.USER_NOT_EXIST, "message": "用户不存在"},

#     {"code": ERROR_CODE.PARAMETER_MISSING, "message": "参数缺失"},
#     {"code": ERROR_CODE.SMS_CODE_IS_INVALID, "message": "验证码校验失败"},
#     {"code": ERROR_CODE.USER_CREATE_FAILURE, "message": "用户创建失败"},
#     {"code": ERROR_CODE.GET_SMS_CODE_FAILUE, "message": "获取验证码失败"},
#     {"code": ERROR_CODE.GET_SMS_CODE_FREQUENTLY, "message": "获取验证码频繁"},
#     {"code": ERROR_CODE.SMS_CODE_INVALID, "message": "验证码校验失败"},
#     {"code": ERROR_CODE.UNSOUPPORT_LOGIN_METHOD, "message": "不支持的登录方式"},
#     {"code": ERROR_CODE.PHONE_IS_ALREADY_REGISTER, "message": "该手机号码已注册"},
#     {"code": ERROR_CODE.USER_OR_PASSWORD_IS_INVALID, "message": "用户名或密码错误"},
#     {"code": ERROR_CODE.LOGIN_FAILURE, "message": "用户登录失败"},
#     {"code": ERROR_CODE.GET_OAUTH_RIGHT_FAILUE, "message": "获取授权失败"},
#     {"code": ERROR_CODE.USER_IS_ALREADY_BIND_PHONE, "message": "用户已经绑定用户"},
#     {"code": ERROR_CODE.PLEASE_INVALID_OLD_PHONE, "message": "请校验旧手机号码"},
#     {"code": ERROR_CODE.UPDATE_PHONE_FAILURE, "message": "手机修改失败"},
#     {"code": ERROR_CODE.UPDATE_PASSWORD_FAILURE, "message": "密码修改失败"},
#     {"code": ERROR_CODE.COMPANY_INFO_NOT_FOUND, "message": "公司资料没有找到"},


#     {"code": ERROR_CODE.WAREHOUSE_NOT_FOUND, "message": "仓库不存在"},
#     {"code": ERROR_CODE.WAREHOUSE_CREATE_FAILURE, "message": "仓库创建失败"},
#     {"code": ERROR_CODE.ALREADY_FAVORITE_THIS_WAREHOUSE, "message": "已收藏该仓库"},

#     {"code": ERROR_CODE.FUNCTION_LIST_ERROR, "message": "获取功能列表失败"},
#     {"code": ERROR_CODE.DEPARTMENT_LIST_ERROR, "message": "获取部门列表失败"},
#     {"code": ERROR_CODE.DEPARTMENT_FUNCTION_LIST_ERROR, "message": "获取部门功能列表失败"},
#     {"code": ERROR_CODE.POSITION_LIST_ERROR, "message": "获取职能列表失败"},
#     {"code": ERROR_CODE.POSITION_FUNCTION_LIST_ERROR, "message": "获取职能功能列表失败"},

#     {"code": ERROR_CODE.USER_ADD_FAILURE, "message": "用户新增失败"},
#     {"code": ERROR_CODE.ACCOUNT_IS_EXIST, "message": "账号已存在"},

#     {"code": ERROR_CODE.WAREHOUSE_CHOICE_NOT_FOUND, "message": "分仓申请不存"},
#     {"code": ERROR_CODE.WAREHOUSE_CHOICE_FAILURE, "message": "分仓申请失败"},
#     {"code": ERROR_CODE.WAREHOUSE_APPROVE_FAILURE, "message": "获取分仓申请列表失败"},
#     {"code": ERROR_CODE.WAREHOUSE_REPORT_FAILURE, "message": "分仓报告失败"},

#     {"code": ERROR_CODE.WAREHOUSE_SERVICE_NOT_FOUND, "message": "仓库服务不存在"},

# ]