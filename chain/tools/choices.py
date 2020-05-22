# 支付信息的选择


pay_choices = (('ALI', '支付宝'), ('BANK', '银行卡'))

trade_status = ((0, '可预定'), (1, '待付款'), (2, '已付款'), (3, '完成'), (4, '取消'), (5, '删除'))

award_sign_in = 'sign'
award_news = 'news'
award_post_advert = 'advert'

award_info_fill = 'personal_information'

award_choices = ((award_sign_in, '注册'), (award_news, '阅读新闻'),
                 ('machine', '机器'), ('trade', '交易'),
                 (award_post_advert, '发布广告'), (award_info_fill, '个人信息认证'))

sell_status = ((0, '待付款'), (1, '已付款'), (3, '取消'), (2, '已完成'))

buy_status = ((0, '待支付'), (1, '已支付'), (3, '取消'), (2, '已完成'))


