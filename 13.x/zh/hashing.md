# 哈希

- [简介](#introduction)
- [配置](#configuration)
- [基本用法](#basic-usage)
    - [密码哈希](#hashing-passwords)
    - [验证密码与哈希值是否匹配](#verifying-that-a-password-matches-a-hash)
    - [判断密码是否需要重新哈希](#determining-if-a-password-needs-to-be-rehashed)
- [哈希算法校验](#hash-algorithm-verification)

<a name="introduction"></a>
## 简介

Laravel 的 `Hash` [门面](/docs/{{version}}/facades) 提供了安全的 Bcrypt 和 Argon2 哈希功能，用于存储用户密码。如果使用 [Laravel 应用入门套件](/docs/{{version}}/starter-kits)，注册和身份认证流程默认会使用 Bcrypt。

Bcrypt 非常适合用于密码哈希，因为它的「工作因子」（计算成本）可以调整。这意味着，随着硬件性能提升，你可以增加生成哈希所需的时间。对于密码哈希而言，慢反而是好事。算法计算密码哈希所需的时间越长，恶意用户生成包含所有可能字符串哈希值的「彩虹表」就越费时，而这些彩虹表可能被用来对应用实施暴力破解。

<a name="configuration"></a>
## 配置

默认情况下，Laravel 使用 `bcrypt` 哈希驱动对数据进行哈希处理。此外，Laravel 还支持其他多种哈希驱动，包括 [argon](https://en.wikipedia.org/wiki/Argon2) 和 [argon2id](https://en.wikipedia.org/wiki/Argon2)。

可以通过 `HASH_DRIVER` 环境变量指定应用使用的哈希驱动。如果希望自定义 Laravel 的所有哈希驱动选项，则应使用 `config:publish` Artisan 命令发布完整的 `hashing` 配置文件：

```shell
php artisan config:publish hashing
```

<a name="basic-usage"></a>
## 基本用法

<a name="hashing-passwords"></a>
### 密码哈希

可以调用 `Hash` 门面的 `make` 方法，对密码进行哈希处理：

```php
<?php

namespace App\Http\Controllers;

use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;

class PasswordController extends Controller
{
    /**
     * 更新用户的密码。
     */
    public function update(Request $request): RedirectResponse
    {
        // 验证新密码的长度……

        $request->user()->fill([
            'password' => Hash::make($request->newPassword)
        ])->save();

        return redirect('/profile');
    }
}
```

<a name="adjusting-the-bcrypt-work-factor"></a>
#### 调整 Bcrypt 工作因子

如果使用 Bcrypt 算法，可以通过 `make` 方法的 `rounds` 选项调整算法的工作因子。不过，Laravel 默认的工作因子已适用于大多数应用：

```php
$hashed = Hash::make('password', [
    'rounds' => 12,
]);
```

<a name="adjusting-the-argon2-work-factor"></a>
#### 调整 Argon2 工作因子

如果使用 Argon2 算法，可以通过 `make` 方法的 `memory`、`time` 和 `threads` 选项调整算法的工作因子。不过，Laravel 提供的默认值已适用于大多数应用：

```php
$hashed = Hash::make('password', [
    'memory' => 1024,
    'time' => 2,
    'threads' => 2,
]);
```

> [!NOTE]
> 有关这些选项的更多信息，请参阅 [PHP 官方 Argon 哈希文档](https://secure.php.net/manual/en/function.password-hash.php)。

<a name="verifying-that-a-password-matches-a-hash"></a>
### 验证密码与哈希值是否匹配

`Hash` 门面提供的 `check` 方法可用于验证给定的明文字符串是否与给定的哈希值匹配：

```php
if (Hash::check('plain-text', $hashedPassword)) {
    // 密码匹配……
}
```

<a name="determining-if-a-password-needs-to-be-rehashed"></a>
### 判断密码是否需要重新哈希

`Hash` 门面提供的 `needsRehash` 方法可用于判断哈希器当前使用的工作因子与生成密码哈希时所用的工作因子是否不同。一些应用会在身份认证过程中执行这项检查：

```php
if (Hash::needsRehash($hashed)) {
    $hashed = Hash::make('plain-text');
}
```

<a name="hash-algorithm-verification"></a>
## 哈希算法校验

为防止哈希算法被篡改，Laravel 的 `Hash::check` 方法会先验证给定的哈希值是否由应用所选的哈希算法生成。如果算法不同，就会抛出 `RuntimeException` 异常。

这种行为符合大多数应用的预期：这些应用的哈希算法通常不会变化，出现不同的算法可能意味着恶意攻击。不过，如果需要在应用中支持多种哈希算法，例如从一种算法迁移到另一种算法时，可以将 `HASH_VERIFY` 环境变量设置为 `false`，禁用哈希算法校验：

```ini
HASH_VERIFY=false
```
