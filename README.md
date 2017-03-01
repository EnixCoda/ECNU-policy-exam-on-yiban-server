# ECNU形势政策考试(易班)服务端程序

简单介绍一下项目文件功能：

`go.php` 过滤客户端请求(POST方式，请求字段为username和password)，调用`go.py`(个人使用可忽略该文件)

`go.py` 向易班提交答卷、统计错题

本项目曾经过2016暑期形势政策考试期间共计500余名同学的使用，较为可靠。

现在开源请有兴趣的同学帮助维护、强化功能(自定义分数等)、提高质量(作者不太熟悉PHP和Python，写的很烂)

欢迎issue讨论/提交pull request

如何使用：

1. 安装 [Python 2.7](https://www.python.org/downloads/)
2. 安装 [requests插件](http://docs.python-requests.org/zh_CN/latest/user/install.html#install)
3. 通过命令行进入`go.py`所在目录，运行`python go.py [账号] [密码]`命令
4. 前几次运行分数将会较低，因为缺少题库数据(运行后存放于`answer.json`文件)，属于正常情况

如需开放给他人使用，请根据`go.php`搭建客户端页面

如有问题，欢迎在issue交流

祝你好运！
