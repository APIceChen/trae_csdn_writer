# 样本输入：n8n 自动化工作流部署实战

## 📌 元数据
- **原始URL**: https://blog.csdn.net/Pocker_Spades_A/article/details/160548769
- **文章类型**: 技术教程/部署指南
- **核心主题**: n8n + DeepSeek + cpolar 从零搭建 AI 工作流系统
- **目标读者**: 开发者、运维工程师、技术爱好者
- **用户需求**: 简化行文进行洗稿，保持技术完整性

---

## 原始内容摘要（精简版）

### 项目背景

n8n 是一款开源、低代码、可视化的自动化工作流引擎。本次实战包含两大模块：
1. **本地部署 n8n + AI 接入**：使用 DeepSeek 跑通对话流
2. **配合 cpolar 做公网穿透**：让 Webhook 能从外部触发本地工作流

### 核心价值主张

- 解决脚本维护困难的问题（变量混乱、注释缺失）
- 用拖拽节点代替写代码
- 数据自主可控 + 成本为零 + 扩展性强
- 300+ 原生集成覆盖主流工具

### 技术栈

- **n8n**: 自动化工作流引擎（核心）
- **Docker**: 容器化部署
- **DeepSeek API**: AI 对话能力
- **cpolar**: 内网穿透工具
- **Linux (CentOS)**: 操作系统

### 主要章节

1. **环境准备**：Docker 安装（6步流程，含镜像加速配置）
2. **n8n 部署**：容器启动、参数配置、初始化设置
3. **实战一 - AI 对话**：DeepSeek API 接入、第一个工作流
4. **实战二 - 网页抓取**：HTTP Request + HTML 提取节点
5. **cpolar 内网穿透**：安装、隧道创建、公网访问
6. **固定域名配置**：二级子域名保留和绑定

### 关键技术要点

#### Docker 镜像加速器（必配！）

```json
{
    "registry-mirrors": [
        "https://docker.xuanyuan.me",
        "https://docker.m.daocloud.io"
    ]
}
```

#### n8n 容器启动命令关键参数

```bash
docker run -d \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  -e N8N_BASIC_AUTH_ACTIVE=true \
  -e N8N_BASIC_AUTH_USER=admin \
  -e N8N_BASIC_AUTH_PASSWORD=YourStrongPassword123! \
  -e TZ=Asia/Shanghai \
  -e N8N_COOKIE_SECURE=false \
  -e N8N_SECURE_COOKIE=false \
  --restart always \
  n8nio/n8n:latest
```

**重要参数说明**：
- `COOKIE_SECURE=false`: 避免登录问题
- `restart always`: 开机自启+异常重启
- 密码必须修改为强密码！

#### DeepSeek API 注意事项

1. 免费额度适合学习测试
2. **密钥只显示一次**，必须立即保存
3. 在 n8n 中选择 DeepSeek 凭证类型

#### cpolar 隧道配置

```yaml
协议: http
本地端口: 5678
地区: China Top
域名类型: 二级子域名(固定) > 随机域名
```

### 适用场景

- 定时任务自动化（数据同步、报表生成）
- 事件驱动流程（表单提交→处理→通知）
- AI 能力集成（智能客服、文本处理）
- 远程开发调试（异地访问本地服务）

### 安全提醒

1. 务必使用强密码
2. API Key 不要提交到公开仓库
3. 生产环境建议启用 HTTPS
4. 定期更新镜像和安全补丁

---

## 关键要点提取

1. **核心价值**: 可视化编排 + AI 能力 + 公网访问
2. **技术亮点**: Docker部署、DeepSeek接入、cpolar穿透
3. **目标受众**: 有基础Linux/Docker能力的新手到中级用户
4. **差异化优势**: 完整的从零到一流程，含两个实战案例
5. **使用门槛**: 中等（需要一定技术基础但步骤详细）

---

## 用户改写要求

- ✅ **简化行文**：删除冗余描述，保留核心技术干货
- ✅ 保持技术准确性：所有命令代码100%正确
- ✅ 采用 CSDN 教程风格：循序渐进、详细但不啰嗦
- ✅ 突出踩坑点：镜像加速、Cookie设置、API Key保存
- ✅ 包含完整的6大模块结构
- ✅ 字数控制在2500-3500字（精简版）
