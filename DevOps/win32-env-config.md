
#windows配置策略运行环境

下载 anaconda 32位版本

Svn 下载 Tibet代码 

## 复制生成新的Conda环境： 
 <pre>
conda create —name pytibet —clone base
conda env list                  查看环境列表
conda activate pytibet      激活环境
conda deactivate              退出环境

</pre>

## 安装python依赖包

<pre>
cd Tibet/mantis
pip install -r ./requirements.txt

</pre>

## 配置数据库


```
monogod --dbpath --bind x.x.x.x 
reids-server 

----
etc/settings.yaml

windows/system32/drivers/etc/hosts

x.x.x.x mongodb
x.x.x.x redis

```

## 账户配置

<pre>
cd Tibet/StrategyRunner/tests
python ./test-config-init-data.py 
 
</pre>
