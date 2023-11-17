

```shell script
#打包
docker build -t switches.keyboard .
#运行
docker run -d --name switches.keyboard -p 8002:8002 \
  -v /home/switches.keyboard/content:/usr/main/content
  switches.keyboard
```

```shell script
docker build -t registry.cn-hangzhou.aliyuncs.com/crow1024/switches.keyboard:1 .
```