
# 加密

- [简介](#introduction)
- [配置](#configuration)
  - [优雅地轮换加密密钥](#gracefully-rotating-encryption-keys)
-   [使用加密器](#using-the-encrypter)

## 简介

Laravel 的加密服务通过使用 AES-256 和 AES-128 加密方式、借助 OpenSSL，提供了一个简单、便捷的加密与解密文本的接口。Laravel 所有加密后的值都使用消息认证码（MAC）进行签名，以确保这些值在加密后不会被修改或篡改。

## 配置

在使用 Laravel 的加密器之前，你必须在配置文件 `config/app.php` 中设置 `key` 配置项。这个配置值由环境变量 `APP_KEY` 所驱动。你应该使用命令 `php artisan key:generate` 来生成该变量的值，因为 `key:generate` 命令会使用 PHP 的安全随机字节生成器来构建一个符合加密安全性的密钥。通常，在 [Laravel 安装](/docs/laravel/12.x/installation) 过程中，这个 `APP_KEY` 环境变量的值会被自动生成。

### 优雅地轮换加密密钥

如果你更改了应用程序的加密密钥，所有已认证的用户会被登出应用程序。这是因为包括会话 Cookie 在内的每个 Cookie 都是由 Laravel 加密的。此外，之前使用旧加密密钥加密的数据将无法再被解密。

为缓解这个问题，Laravel 允许你在应用程序的 `APP_PREVIOUS_KEYS` 环境变量中列出之前的加密密钥。这个变量可以包含以逗号分隔的所有旧加密密钥列表：

```ini
APP_KEY="base64:J63qRTDLub5NuZvP+kb8YIorGS6qFYHKVo6u7179stY="
APP_PREVIOUS_KEYS="base64:2nLsGFGzyoae2ax3EF2Lyq/hH6QghBGLIq5uL+Gp8/w="
```



当你设置这个环境变量时，Laravel 在加密值时将始终使用 「当前」 的加密密钥。然而，在解密值时，Laravel 首先会尝试当前密钥，如果使用当前密钥解密失败，Laravel 将尝试所有之前的密钥，直到其中一个密钥能够解密该值。

这种优雅解密的方法允许用户即使在加密密钥轮换后也能继续不间断地使用你的应用程序。

<a name="using-the-encrypter"></a>
## 基本用法

<a name="encrypting-a-value"></a>
#### 加密一个值

你可以使用 `Crypt` 门面提供的 `encryptString` 方法来加密一个值。所有加密的值都是使用 OpenSSL 和 AES-256-CBC 加密算法加密的。此外，所有加密的值都会使用消息认证码（MAC）进行签名。集成的消息身份验证码将阻止被恶意用户篡改的任何值的解密：

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

你可以使用 `Crypt` 门面提供的 `decryptString` 方法来解密值。如果值无法正确解密，例如当消息认证码无效时，将会抛出一个 `Illuminate\Contracts\Encryption\DecryptException` 异常。

```php
use Illuminate\Contracts\Encryption\DecryptException;
use Illuminate\Support\Facades\Crypt;

try {
    $decrypted = Crypt::decryptString($encryptedValue);
} catch (DecryptException $e) {
    // ...
}
```
