from tortoise import fields
from tortoise.models import Model

class testdemo(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "test_table1"
        table_description = "测试表"

    def __str__(self):
        return self.name
    

class testdemo2(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)            
    
    class Meta:
        table = "test_table2"
        table_description = "测试表2"

    def __str__(self):
        return self.name



