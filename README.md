# CtrlCV — 学术简历助手

申请基金、报奖项、找工作，总要列论文。

CtrlCV 可从 YAML 文献库里复制纯文本信息到剪贴板。

左栏期刊，右栏论文。按 `-` 或者 `:`，复制一条信息。按分隔符按钮，拼接列表再复制。

## 用法

### 1. 安装依赖

```bash
pip install pyyaml
```

### 2. 准备文献库

**Journals.yaml**

```yaml
- Nature:
    名称: Nature
    文章:
        - 深度学习在药物发现中的应用
```

**Papers.yaml**

```yaml
- 深度学习在药物发现中的应用:
    标题: 深度学习在药物发现中的应用
    年份: 2021
    期刊: Nature
    作者:
        - 张三:
            第一作者: 是
        - 李四
    关键词:
        - 深度学习
        - 药物发现
```

### 3. 运行

```bash
python CtrlCV.py
```

生成 **ExCiting.html**，打开便可复制。

## 作者

- DeepSeek v3.2

- Yu-Chang Yang \*
