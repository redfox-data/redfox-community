# TikTok 用户关注列表与用户搜索 — API 规格

本 Skill 包含两个接口：`userFollowing`（关注列表查询）与 `searchUser`（关键词搜索用户）。

**`POST`** `https://redfox.hk/story/api/tiktok/ability/userFollowing`

---

## 接口说明

按 `userId`（纯数字）或 `secUserId`（字母数字混合）查询指定 TikTok 用户的关注列表，返回关注对象的账号画像与分页游标。

- **Method**: `POST`
- **Host**: `https://redfox.hk`
- **Path**: `/story/api/tiktok/ability/userFollowing`
- **成功码**: `code=2000`

---

## 请求头

| 名称 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| REDFOX_API_KEY | string | 是 | API 密钥，格式 `ak_xxxxxxxx`，通过环境变量 `REDFOX_API_KEY` 注入 |
| Content-Type | string | 是 | 固定 `application/json` |

> 注意：本接口鉴权头名为 `REDFOX_API_KEY`（不是同域 `topicAwemeList` 使用的 `X-API-KEY`）。

---

## 请求参数

| 参数 | 类型 | 必填 | 说明 | 示例 |
| --- | --- | --- | --- | --- |
| userId | string | 二选一 | 纯数字用户ID，与 secUserId 二选一 | 6748953635118187521 |
| secUserId | string | 二选一 | 字母数字混合ID（`MS4wLjAB` 开头），与 userId 二选一 | MS4wLjABAAAA... |
| minTime | string | 是 | 翻页游标，首次传 `0`，后续传上次返回的 `minTime` | 0 |
| pageToken | string | 是 | 翻页token，首次传空字符串，后续传上次返回的 `pageToken` | — |
| source | string | 是 | 请求来源标识，固定为 `TikTok关键词搜用户-GitHub` | TikTok关键词搜用户-GitHub |

> 本接口不接受 @handle / 昵称查询；用户仅提供 handle 时需先引导其提供数字 userId 或 secUserId。

---

## 响应字段

| 字段 | 类型 | 说明 | 示例 |
| --- | --- | --- | --- |
| code | integer | 响应状态码，2000 表示成功 | 2000 |
| msg | string | 响应消息 | 成功 |
| data | object | 数据体 | — |
| data.followingList | array | 关注用户列表 | — |
| followingList[].avatarImage | string | 用户头像URL | https://p16-common-sign.tiktokcdn-eu.com/... |
| followingList[].createTime | integer | 账号注册时间（Unix时间戳，秒级） | 1710440934 |
| followingList[].customVerify | string | 个人认证说明 | — |
| followingList[].enterpriseVerifyReason | string | 企业认证说明 | — |
| followingList[].fansCount | integer | 粉丝数 | 100404 |
| followingList[].favoritingCount | integer | 点赞过的视频数 | 585 |
| followingList[].followCount | integer | 该用户的关注数 | 21 |
| followingList[].isSecret | integer | 是否为私密账号：0-否，1-是 | 0 |
| followingList[].likedTotal | integer | 作品累计获赞总数 | 227161 |
| followingList[].region | string | 用户所属地区 | US |
| followingList[].secUserId | string | 加密用户ID | MS4wLjABAAAAYvgx... |
| followingList[].signature | string | 个性签名（可能含换行符） | — |
| followingList[].userHandle | string | 用户handle | cnliziqi |
| followingList[].userId | string | 用户数字ID | 7346287701194900513 |
| followingList[].userName | string | 用户昵称 | 李子柒 |
| followingList[].workCount | integer | 发布的作品数量 | 143 |
| data.hasMore | integer | 是否还有更多数据：1-有，0-无 | 1 |
| data.minTime | string | 当前列表最小时间戳（字符串），翻页游标，传入下次请求获取更早数据 | 1760525119 |
| data.pageToken | string/null | 分页令牌，可能为 null | — |

---

## 响应示例

```json
{
  "code": 2000,
  "data": {
    "followingList": [
      {
        "avatarImage": "https://p16-common-sign.tiktokcdn-eu.com/tos-useast2a-avt-0068-euttp/xxx.heic",
        "createTime": 1710440934,
        "customVerify": "",
        "enterpriseVerifyReason": "",
        "fansCount": 100404,
        "favoritingCount": 585,
        "followCount": 21,
        "isSecret": 0,
        "likedTotal": 227161,
        "region": "US",
        "secUserId": "MS4wLjABAAAAYvgxoNf0HsCmVhlSF5evwYvT3-Q0Zul4gUGzEytIWt_mazK7xDkVGheeQaYT7WRL",
        "signature": "",
        "userHandle": "user1203173161520",
        "userId": "7346287701194900513",
        "userName": "user1203173161520",
        "workCount": 143
      },
      {
        "avatarImage": "https://p16-common-sign.tiktokcdn-eu.com/tos-alisg-avt-0068/xxx.heic",
        "createTime": 1571897644,
        "customVerify": "原創美食視頻自媒體",
        "enterpriseVerifyReason": "",
        "fansCount": 3754224,
        "favoritingCount": 1,
        "followCount": 0,
        "isSecret": 0,
        "likedTotal": 31904748,
        "region": "US",
        "secUserId": "MS4wLjABAAAAEjxOaFdz-EXDYWI2Qz9X6uxMQeQIKaAzkAWyInZ6M309-FuHzhDzDAIyUaVRxLME",
        "signature": "李家有女，人称子柒\nOfficial Account， no distribution channels outside China mainland",
        "userHandle": "cnliziqi",
        "userId": "6748953635118187521",
        "userName": "李子柒",
        "workCount": 785
      }
    ],
    "hasMore": 1,
    "minTime": "1760525119",
    "pageToken": null
  },
  "msg": "成功"
}
```

---

# 关键词搜索用户（searchUser）

**`POST`** `https://redfox.hk/story/api/tiktok/ability/searchUser`

按昵称 / handle 等关键词搜索 TikTok 用户，返回账号画像与分页游标。典型用途：为关注列表查询定位目标账号的 `userId` / `secUserId`。

## 请求头

| 名称 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| REDFOX_API_KEY | string | 是 | API 密钥，格式 `ak_xxxxxxxx`，通过环境变量 `REDFOX_API_KEY` 注入 |
| Content-Type | string | 是 | 固定 `application/json` |

## 请求参数

| 参数 | 类型 | 必填 | 说明 | 示例 |
| --- | --- | --- | --- | --- |
| keyword | String | 是 | 搜索关键词（昵称 / handle） | 南浔 |
| offset | String | 是 | 偏移量，首页传 `"0"`，翻页传上次返回的 `cursor` | 0 |
| count | String | 是 | 单页条数 | 20 |
| followerCountFilter | Integer | 否 | 粉丝数筛选：空-不限制 / 1-0~1K / 2-1K~10K / 3-10K~100K / 4-100K以上 | — |
| profileTypeFilter | Integer | 否 | 账号类型筛选：空-不限制 / 1-认证用户 | — |
| otherPrefFilter | Integer | 否 | 其他偏好：空-不限制 / 1-按用户名相关性 | — |
| source | String | 是 | 请求来源标识，固定为 `TikTok关键词搜用户-GitHub` | TikTok关键词搜用户-GitHub |

## 响应字段

| 字段 | 类型 | 说明 | 示例 |
| --- | --- | --- | --- |
| code | Integer | 响应状态码，2000 表示成功 | 2000 |
| msg | String | 响应消息 | 成功 |
| data | Object | 数据体 | — |
| data.cursor | Integer | 下一页游标，翻页时传入下次请求的 `offset` | 20 |
| data.hasMore | Integer | 是否有更多数据：1-有，0-无 | 1 |
| data.userList | Array | 用户列表 | — |
| userList[].avatarImage | string | 用户头像URL | https://sf16-passport-va.ibytedtos.com/... |
| userList[].fansCount | Integer | 粉丝数 | 47 |
| userList[].followCount | Integer | 关注数 | 69 |
| userList[].likedTotal | Integer | 获赞总数 | 0 |
| userList[].secUserId | String | 用户安全ID（加密，`MS4wLjAB` 开头） | MS4wLjABAAAAzE8d... |
| userList[].userHandle | String | 用户唯一TikTok号 | user976316235 |
| userList[].userId | String | 用户原始数字ID | 6802494138883802114 |
| userList[].userName | String | 用户昵称 | 南浔 |
| userList[].workCount | Integer | 作品数量 | 0 |

> 注：`userList[]` 实测还会返回 `followCount`（该用户关注数），可如实展示；该接口无认证信息字段。

## 响应示例

```json
{
  "code": 2000,
  "data": {
    "cursor": 20,
    "hasMore": 1,
    "userList": [
      {
        "avatarImage": "https://sf16-passport-va.ibytedtos.com/img/user-avatar-musical...",
        "fansCount": 47,
        "followCount": 69,
        "likedTotal": 0,
        "secUserId": "MS4wLjABAAAAzE8dVYNVlicoaifT-T50a10K-AMdw2tw5QzimiDwXd3eiAq9Fi8zFIuHdTK24_lK",
        "userHandle": "user976316235",
        "userId": "6802494138883802114",
        "userName": "南浔",
        "workCount": 0
      }
    ]
  },
  "msg": "成功"
}
```

---

## 错误码

| code | 含义 | 处理 |
| --- | --- | --- |
| 2000 | 成功 | 正常输出 |
| 3105 | API Key 已禁用 | 提示更换有效 Key，输出 API Key 获取提醒，不重复重试 |
| 3203 | 参数校验失败 | 按返回 `msg` 提示修正参数（此类错误通常不扣积分） |

---

## 密钥获取与安全说明

- 本 API 需要使用 API 密钥 `REDFOX_API_KEY`，由 [红狐 hub](https://redfox.hk/settings/api-keys?source=github) 提供。
- 前往红狐 hub 注册并登录，在密钥管理模块创建 API 密钥，复制并仅在请求头中使用。
- 禁止在代码、提示词、日志或输出文件中硬编码/明文暴露密钥；统一通过环境变量注入。

---

## 传输层说明

redfox.hk 在当前本地链路实测要求**无 SNI 的 socket + SSL 连接**，标准 HTTP 客户端（curl / requests / urllib）可能静默卡至超时或握手失败。脚本 `scripts/fetch_user_following.py` 已内置该传输方式：

- 使用 raw socket 建立连接，TLS 握手不携带 SNI（`server_hostname=None`）；
- 保留证书链校验，仅关闭 hostname 检查（`check_hostname = False`）以兼容无 SNI 握手；
- 该降级仅限定作用于 redfox.hk 域名的请求，属已实测确认的端点传输要求。
