# 原始文章内容 - n8n 自动化工作流部署实战

## 元数据
- **原始URL**: https://blog.csdn.net/Pocker_Spades_A/article/details/160548769
- **原始标题**: n8n自动化工作流引擎部署与AI接入实战
- **作者**: Pocker_Spades_A
- **抓取日期**: 2026-05-28
- **处理状态**: ✅ 已抓取

---

## 前言

写脚本这事，干过的都知道：当时写完跑通了，过三个月回头看，自己都看不懂自己当初写的什么。变量命名混乱、注释残缺、错误处理基本没有——维护成本比写的时候还高。更别提团队协作了，你改一行我改一行，最后谁都不敢动，一动就崩。

**n8n** 正是来解决这个问题的。它是一款开源、低代码、可视化的自动化工作流引擎，核心理念是：用拖拽节点代替写代码，用图形化界面代替看日志。

和 Zapier、Make 这类商业自动化工具相比，n8n 的优势在于三点：**数据自主可控**、**成本为零**、**扩展性强**。你可以部署在自己的服务器上，配置文件在自己手里，不存在第三方跑路或者涨价的问题。300+ 的原生集成覆盖了主流的 IM、表格、数据库、API 服务，常用的场景基本都能覆盖。

这次实战分两块：一块是**本地部署 n8n + AI 接入**（用 DeepSeek 跑通对话流），另一块是**配合 cpolar 做公网穿透**，让 Webhook 能从外部触发本地工作流。

整个流程不复杂，按步骤走，新手也能一次跑通。

## 1.什么是n8n

n8n（发音为 "n-eight-n"）是一款开源、可自托管、低代码的自动化工作流引擎，旨在帮助个人和团队轻松连接不同的应用程序与服务，实现高效、灵活的任务自动化。

### 核心特点

* 开源免费 - 基于MIT许可证，代码完全公开，无隐藏收费，无厂商锁定。
* 可自托管 - 支持部署在本地服务器、Docker、Kubernetes或云平台，数据完全由你掌控，保障隐私与安全。
* 可视化流程编排 - 通过直观的拖拽式界面，用"节点"（Nodes）连接触发器与操作，像搭积木一样构建复杂自动化逻辑，无需写代码（也支持JavaScript自定义函数）。
* 300+ 原生集成 - 支持Slack、飞书、企业微信、Notion、Google Sheets、MySQL、PostgreSQL、Webhook、AWS、Telegram、Zapier等主流工具，轻松打通数据孤岛。
* 高度可扩展 - 可开发自定义节点，或使用社区贡献的插件，满足个性化需求。

### 典型应用场景

* 自动将表单提交数据存入数据库并发送邮件通知
* 监控服务器状态，异常时通过钉钉/Telegram告警
* 同步多平台客户信息到CRM系统
* 构建内部审批流：飞书 → 数据库 → 邮件归档
* 替代Zapier / Make，节省成本，提升可控性

### 为什么选择n8n？

| 特性   | n8n        | 商业自动化（如 Zapier）  |
| ---- | ---------- | ---------------- |
| 开源   | ✅ 是        | ❌ 否              |
| 自托管  | ✅ 支持       | ❌ 仅 SaaS         |
| 成本   | 💰 免费（自托管） | 💳 按任务收费         |
| 数据隐私 | 🔒 完全私有    | ☁️ 存于第三方服务器      |
| 灵活性  | ⚙️ 支持自定义代码 | ⚠️ 功能受限，不支持自定义代码 |

## 2.准备工作

若你的系统尚未安装Docker，请先一键安装：

### 2.1 卸载旧版Docker（若有）

```bash
yum remove docker docker-client docker-client-latest docker-common docker-latest docker-latest-logrotate docker-logrotate docker-engine
```

### 2.2 安装依赖包

```bash
yum install -y yum-utils device-mapper-persistent-data lvm2
```

### 2.3 添加Docker国内源

```bash
yum-config-manager --add-repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
```

### 2.4 安装Docker并启动：

```bash
yum install -y docker-ce docker-ce-cli containerd.io
systemctl start docker
systemctl enable docker  # 开机自启
docker --version  # 显示版本即成功
```

### 2.5 配置Docker国内速（必做，解决拉取失败）

新建/etc/docker/daemon.json文件，增加如下内容：

```json
{
    "registry-mirrors": [
        "https://docker.xuanyuan.me",
        "https://docker.m.daocloud.io",
        "https://docker.imgdb.de",
        "https://docker-0.unsee.tech"
    ]
}
```

### 2.6 应用配置并重启Docker服务

```bash
systemctl daemon-reload
systemctl restart docker
```

## 3.部署n8n

### 3.1 安装n8n

在线手动拉取n8n最新镜像（便于查看进度）：

```bash
docker pull n8nio/n8n:latest
```

创建数据目录（避免容器删除后数据丢失）：

```bash
mkdir -p ~/.n8n
chmod -R 777 ~/.n8n  # 赋予读写权限
```

启动n8n容器（后台运行 + 开机自启 + 基础认证）：

参数解析:
- N8N_COOKIE_SECURE=false # 关键：禁用Secure Cookie，取消安全Cookie强制要求
- N8N_SECURE_COOKIE=false # 兼容旧版本n8n的参数
- N8N_BASIC_AUTH_USER=admin # 自定义管理员账号
- N8N_BASIC_AUTH_PASSWORD=YourStrongPass123! # 自定义强密码
- TZ=Asia/Shanghai #适配中国时区
- restart always #异常自动重启+开机自启

```bash
docker run -d  --name n8n -p 5678:5678 -v ~/.n8n:/home/node/.n8n -e N8N_BASIC_AUTH_ACTIVE=true -e N8N_BASIC_AUTH_USER=admin -e N8N_BASIC_AUTH_PASSWORD=root@1234 -e TZ=Asia/Shanghai   -e N8N_COOKIE_SECURE=false -e N8N_SECURE_COOKIE=false --restart always n8nio/n8n:latest
```

查看容器状态：

```bash
docker ps | grep n8n
```

访问n8n界面：

打开浏览器输入http://服务器IP:5678

### 3.2 初始化n8n

使用自己的邮箱及用户名密码登录到n8n主页：

登录成功后填写一下基础背调：

获取永久免费密钥：

在"settings"中，找到"Usage and plan"中添加刚刚获取的永久免费密钥：

至此初始化成功！

## 4.玩转n8n实战

### 4.1 搭建第一个n8n工作流（接入AI）

为了让我们的n8n工作流能够与AI对话，我们需要一个AI服务的API密钥。本次我们选用**DeepSeek**作为AI服务提供商。DeepSeek提供了强大的语言模型，并且有免费的API调用额度，非常适合学习和测试。

1. 注册账号 - 访问DeepSeek开放平台，点击"注册"，按照页面提示完成账号创建。

2. 获取API密钥 - 登录你的DeepSeek平台账号。在左侧导航栏中找到 "API密钥"（或类似名称的选项）。点击 "创建新的API密钥"。为密钥设置一个便于识别的名称（例如：n8n），然后确认创建。

3. 重要提示 - 创建成功后，系统将仅显示一次完整的API密钥。请务必立即复制并将其保存在安全的位置（如密码管理器或加密的本地文件中）。若不慎丢失，无法找回，只能重新生成新密钥。

**新建工作流**

在n8n仪表板点击"Create Workflow"，添加作为触发器节点：

点击加号选择节点：

继续如图操作：

**添加AI节点**

点击触发器节点的号，搜索AI Agent：

配置AI模型：

选择deepseek，填入密钥：

回到画布，开始验证，点击open chat ;

给 AI 发一条信息：

收到有效响应即验证成功。

**🎉 恭喜你！当AI给出回答，说明所有的准备工作已完成，并且你成功搭建并运行了你的第一个n8n AI工作流！🎉**

### 4.2搭建第二个工作流（网页抓取）

**创建新工作流：在n8n面板点击"创建工作流"**，进入可视化编辑界面：

点击加号选择节点：

继续如图操作：

**添加AI节点**

点击触发器节点的号，搜索AI Agent：

搜索"http"并添加：

添加HTTP请求节点并连接至触发节点。在参数窗口设置请求方法为GET，**目标网址**填入https://scrapeme.live/shop/

添加一个HTML节点并选择**"提取HTML内容"**操作。

测试验证：返回主界面点击"执行工作流"，成功节点将显示绿色边框。若出现红色提示或数据异常，请检查参数设置与网页结构，或查阅官方文档。

[n8n](https://n8n.io/) 是一款强大的开源自动化工具，支持在本地快速搭建工作流。但当你希望从外部（如手机、远程服务器或第三方服务）触发本地n8n时，往往会遇到内网无法被公网访问的难题。

这时候，[cpolar](https://www.cpolar.com/) 就派上了大用场！

cpolar是一款简单高效的内网穿透工具，无需公网 IP、无需复杂配置，只需一条命令，就能将你本地运行的n8n服务安全地映射到公网URL。

为什么选择cpolar搭配n8n？

* 零门槛上手：下载即用，5秒创建HTTPS隧道
* 自动HTTPS：免费提供带有效证书的地址，完美兼容Webhook安全要求
* 稳定可靠：支持后台常驻、断线重连，适合长期运行自动化任务
* 隐私可控：数据经加密隧道传输，不经过第三方中转（企业版支持私有部署）

跟我一起安装cpolar吧！

## 5.安装cpolar实现随时随地开发

### 5.1 什么是cpolar？

cpolar是一款安全高效的内网穿透工具，无需公网IP或复杂配置，只需一条命令，即可将本地服务器、Web服务或任意端口映射到公网，让你随时随地远程访问内网应用，特别适合开发调试、远程运维和应急部署等场景。

### 5.2 部署cpolar

cpolar 可以将你本地电脑中的服务（如 SSH、Web、数据库）映射到公网。即使你在家里或外出时，也可以通过公网地址连接回本地运行的开发环境。

❤️以下是安装cpolar步骤：

使用一键脚本安装命令：

```bash
sudo curl https://get.cpolar.sh | sh
```

安装完成后，执行下方命令查看cpolar服务状态：（如图所示即为正常启动）

```bash
sudo systemctl status cpolar
```

Cpolar安装和成功启动服务后，在浏览器上输入虚拟机主机IP加9200端口即:[http://ip:9200] 访问Cpolar管理界面，使用Cpolar官网注册的账号登录,登录后即可看到cpolar web 配置界面,接下来在web 界面配置即可：

打开浏览器访问本地9200端口，使用cpolar账户密码登录即可,登录后即可对隧道进行管理。

## 6.配置公网地址

登录cpolar web UI管理界面后,点击左侧仪表盘的隧道管理——创建隧道：

* 隧道名称：可自定义，本例使用了:n8n，注意不要与已有的隧道名称重复
* 协议：http
* 本地地址：5678
* 域名类型：随机域名
* 地区：选择China Top

创建成功后,打开左侧在线隧道列表,可以看到刚刚通过创建隧道生成了公网地址，接下来就可以在其他电脑或者移动端设备（异地）上，使用地址访问。

访问成功。

## 7.保留固定公网地址

使用cpolar为其配置二级子域名，该地址为固定地址，不会随机变化。

点击左侧的预留，选择保留二级子域名，地区选择china Top，然后设置一个二级子域名名称，我使用的是n8n，大家可以自定义。填写备注信息，点击保留。

登录cpolar web UI管理界面，点击左侧仪表盘的隧道管理——隧道列表，找到所要配置的隧道，点击右侧的`编辑`。

修改隧道信息，将保留成功的二级子域名配置到隧道中

* 域名类型：选择二级子域名
* Sub Domain：填写保留成功的二级子域名
* 地区: China Top

点击`更新`

更新完成后，打开在线隧道列表，此时可以看到随机的公网地址已经发生变化，地址名称也变成了保留和固定的二级子域名名称。

最后，我们使用固定的公网地址在任意设备的浏览器中访问，可以看到成功访问的页面，这样一个永久不会变化的二级子域名公网网址即设置好了。

## 总结

n8n 这套方案的核心价值在于**把自动化从"写得懂的人才能维护"变成"看得懂流程的人都能改"**。

可视化编排的好处不只是降低门槛，更重要的是**流程即文档**。你搭的工作流长什么样，节点之间什么关系，一截图就能给别人讲明白。接手的人不需要读你三个月前的代码注释，直接看图就行。

实际用下来，有两个场景比较顺手：**定时任务类**（比如每天同步一次数据、每周生成报表）和 **事件触发类**（表单提交触发、收到特定邮件触发）。AI 接入这块，DeepSeek 的免费额度对于学习和测试来说够用了，生产环境再考虑付费。

局限也要说清楚：n8n 本身是事件驱动的，对实时性要求极高的场景不太适合；另外 Docker 部署虽然简单，但后续的更新维护需要一定的 Linux 基础。免费套餐跑个人项目足够了，团队用的话建议上高级版。

配合 cpolar 做公网访问这个组合，适合那些需要接收外部 Webhook 回调的场景——比如第三方服务触发、远程 API 调用之类的。固定二级域名配好之后，地址不用改，还是比较省心的。

如果你有重复性任务需要自动化、愿意花一点时间搭环境，n8n 值得一试。30 分钟入门，能跑第一个工作流，后续慢慢加功能就行。
