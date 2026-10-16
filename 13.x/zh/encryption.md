# 加密

- [简介](#introduction)
- [配置](#configuration)
    - [平滑轮换加密密钥](#gracefully-rotating-encryption-keys)
- [使用加密器](#using-the-encrypter)

<a name="introduction"></a>
## 简介

Laravel 的加密服务通过 OpenSSL，使用 AES-256 和 AES-128 算法，为文本加密与解密提供简单、便捷的接口。Laravel 的所有加密值都会使用消息认证码（MAC）进行签名，以防止其内容在加密后被修改或篡改。

<a name="configuration"></a>
## 配置

使用 Laravel 的加密器之前，必须在 `config/app.php` 配置文件中设置 `key` 配置项。这个配置值由 `APP_KEY` 环境变量指定。应使用 `php artisan key:generate` 命令生成该变量的值，因为 `key:generate` 命令会使用 PHP 的安全随机字节生成器，为应用生成符合密码学安全要求的密钥。通常，`APP_KEY` 环境变量的值会在[安装 Laravel](/docs/{{version}}/installation)时自动生成。

<a name="gracefully-rotating-encryption-keys"></a>
### 平滑轮换加密密钥

如果更改应用的加密密钥，所有已认证用户都会退出登录。这是因为所有 Cookie（包括会话 Cookie）都由 Laravel 加密。此外，之前使用旧密钥加密的数据也将无法再解密。

为缓解这个问题，Laravel 允许你在应用的 `APP_PREVIOUS_KEYS` 环境变量中列出旧的加密密钥。可以将所有旧密钥以逗号分隔后写入这个变量：

```ini
APP_KEY="base64:J63qRTDLub5NuZvP+kb8YIorGS6qFYHKVo6u7179stY="
APP_PREVIOUS_KEYS="base64:2nLsGFGzyoae2ax3EF2Lyq/hH6QghBGLIq5uL+Gp8/w="
```

设置这个环境变量后，Laravel 在加密值时始终使用「当前」加密密钥。解密时，Laravel 会先尝试当前密钥；如果解密失败，就会依次尝试所有旧密钥，直到其中一个密钥能够成功解密该值。

这种兼容旧密钥的解密方式，让用户在密钥轮换后仍能不中断地使用应用。

<a name="using-the-encrypter"></a>
## 使用加密器

<a name="encrypting-a-value"></a>
#### 加密一个值

可以使用 `Crypt` 门面提供的 `encryptString` 方法加密一个值。所有加密值都使用 OpenSSL 和 AES-256-CBC 算法加密。此外，所有加密值都会使用消息认证码（MAC）进行签名。内置的消息认证码校验会阻止解密任何被恶意用户篡改的值：

```php
<?php

namespace App\Http\Controllers;

use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Crypt;

class DigitalOceanTokenController extends Controller
{
    /**
     * 为用户存储一个 DigitalOcean API 令牌。
     */
    public function store(Request $request): RedirectResponse
    {
        $request->user()->fill([
            'token' => Crypt::encryptString($request->token),
        ])->save();

        return redirect('/secrets');
    }
}
```

<a name="decrypting-a-value"></a>
#### 解密一个值

可以使用 `Crypt` 门面提供的 `decryptString` 方法解密值。如果无法正确解密，例如消息认证码无效时，就会抛出 `Illuminate\Contracts\Encryption\DecryptException` 异常：

```php
use Illuminate\Contracts\Encryption\DecryptException;
use Illuminate\Support\Facades\Crypt;

try {
    $decrypted = Crypt::decryptString($encryptedValue);
} catch (DecryptException $e) {
    // ...
}
```
