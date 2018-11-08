from haystack import indexes
from goods.models import SKU


# 创建索引类 格式： <模型类> + Index
class SKUIndex(indexes.SearchIndex, indexes.Indexable):
    # document=True 说明此字段是索引字段
    # user_template=True 说明建立索引数据时 索引字段种包含那些内容最后由模板指明
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        # 返回索引类对应的模型类
        return SKU

    # 返回要建立索引的数据查询集
    def index_queryset(self, using=None):
        return self.get_model().objects.filter(is_launched=True)