"""
数据库模型定义
"""
from peewee import MySQLDatabase, Model, CharField, FloatField, IntegerField, AutoField, DateTimeField
from datetime import datetime
import hashlib
from config import DATABASE_CONFIG


# 数据库连接
db = MySQLDatabase(**DATABASE_CONFIG)


class BaseModel(Model):
    """基础模型类"""
    class Meta:
        database = db


class User(BaseModel):
    """用户模型"""
    id = AutoField(primary_key=True)
    username = CharField(max_length=50, unique=True, verbose_name='用户名')
    password_hash = CharField(max_length=128, verbose_name='密码哈希')
    email = CharField(max_length=100, null=True, verbose_name='邮箱')
    created_at = DateTimeField(default=datetime.now, verbose_name='创建时间')
    updated_at = DateTimeField(default=datetime.now, verbose_name='更新时间')
    is_active = IntegerField(default=1, verbose_name='是否激活')
    
    class Meta:
        table_name = 'users'
    
    def __str__(self):
        return f"User({self.username})"
    
    @classmethod
    def create_user(cls, username, password, email=None):
        """
        创建新用户
        
        Args:
            username (str): 用户名
            password (str): 明文密码
            email (str): 邮箱地址（可选）
            
        Returns:
            User: 创建的用户对象
            
        Raises:
            ValueError: 用户名已存在
        """
        # 检查用户名是否已存在
        if cls.select().where(cls.username == username).exists():
            raise ValueError("用户名已存在")
        
        # 创建密码哈希
        password_hash = cls._hash_password(password)
        
        # 创建用户
        user = cls.create(
            username=username,
            password_hash=password_hash,
            email=email,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        return user
    
    @classmethod
    def authenticate(cls, username, password):
        """
        用户认证
        
        Args:
            username (str): 用户名
            password (str): 明文密码
            
        Returns:
            User or None: 认证成功返回用户对象，失败返回None
        """
        try:
            user = cls.get(cls.username == username, cls.is_active == 1)
            if cls._verify_password(password, user.password_hash):
                # 更新最后登录时间
                user.updated_at = datetime.now()
                user.save()
                return user
            return None
        except cls.DoesNotExist:
            return None
    
    @staticmethod
    def _hash_password(password):
        """
        生成密码哈希
        
        Args:
            password (str): 明文密码
            
        Returns:
            str: 密码哈希
        """
        # 使用SHA256 + 盐值进行哈希
        salt = "douban_movie_salt_2024"  # 生产环境应使用随机盐值
        return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    
    @staticmethod
    def _verify_password(password, password_hash):
        """
        验证密码
        
        Args:
            password (str): 明文密码
            password_hash (str): 存储的密码哈希
            
        Returns:
            bool: 密码是否正确
        """
        return User._hash_password(password) == password_hash
    
    def change_password(self, old_password, new_password):
        """
        修改密码
        
        Args:
            old_password (str): 旧密码
            new_password (str): 新密码
            
        Returns:
            bool: 是否修改成功
        """
        if not self._verify_password(old_password, self.password_hash):
            return False
        
        self.password_hash = self._hash_password(new_password)
        self.updated_at = datetime.now()
        self.save()
        return True
    
    @classmethod
    def get_user_by_username(cls, username):
        """
        根据用户名获取用户
        
        Args:
            username (str): 用户名
            
        Returns:
            User or None: 用户对象或None
        """
        try:
            return cls.get(cls.username == username, cls.is_active == 1)
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def create_table_if_not_exists(cls):
        """创建用户表（如果不存在）"""
        db.create_tables([cls], safe=True)


class Movie(BaseModel):
    """电影模型"""
    id = AutoField(primary_key=True)
    title = CharField(max_length=200, verbose_name='电影名称')
    rating_num = FloatField(verbose_name='评价分数')
    comment_num = IntegerField(verbose_name='评论人数')
    directors = CharField(max_length=200, verbose_name='导演')
    actors = CharField(max_length=200, verbose_name='主演')
    year = CharField(max_length=10, verbose_name='上映年份')
    country = CharField(max_length=100, verbose_name='出品地')
    category = CharField(max_length=100, verbose_name='剧情类别')
    pic = CharField(max_length=500, verbose_name='电影海报链接')

    class Meta:
        table_name = 'douban_movie'

    def __str__(self):
        return f"{self.title} ({self.year})"

    @classmethod
    def create_table_if_not_exists(cls):
        """创建表（如果不存在）"""
        db.create_tables([cls], safe=True)
    
    @classmethod 
    def create_all_tables(cls):
        """创建所有表（如果不存在）"""
        db.create_tables([User, cls], safe=True)

    @classmethod
    def get_movies_by_year(cls, year):
        """根据年份查询电影"""
        return cls.select().where(cls.year == year)

    @classmethod
    def bulk_insert(cls, movies_data):
        """批量插入电影数据"""
        with db.atomic():
            for i in range(0, len(movies_data), 50):
                cls.insert_many(movies_data[i:i + 50]).execute()


def connect_database():
    """连接数据库"""
    try:
        db.connect()
        print("数据库连接成功")
        return True
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return False


def close_database():
    """关闭数据库连接"""
    if not db.is_closed():
        db.close()
        print("数据库连接已关闭") 