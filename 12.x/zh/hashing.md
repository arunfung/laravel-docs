
# 哈希（Hashing）

- [简介](#introduction)
- [配置](#configuration)
- [基础用法](#basic-usage)
    - [密码哈希](#hashing-passwords)
    - [验证密码是否匹配哈希值](#verifying-that-a-password-matches-a-hash)
    - [判断密码是否需要重新哈希](#determining-if-a-password-needs-to-be-rehashed)
- [哈希算法校验](#hash-algorithm-verification)

## 简介

Laravel 的 `Hash` [Facade](/docs/laravel/12.x/facades) 提供了安全的 Bcrypt 与 Argon2 哈希方式，用于存储用户密码。如果你使用的是某个 [Laravel 应用启动套件](/docs/laravel/12.x/starter-kits)，系统默认会使用 Bcrypt 来完成注册和登录认证。

Bcrypt 是非常适合用于密码哈希的选择，因为它的「工作因子」是可调节的 —— 这意味着，随着硬件性能的提升，你可以提高生成哈希的耗时，从而增强安全性。在处理密码哈希时，「慢」反而是件好事。算法越慢，黑客要生成「彩虹表」（即穷举所有字符串的哈希值）用于暴力破解，就越费时。

## 配置

Laravel 默认使用 `bcrypt` 作为哈希驱动。但它也支持其他多种驱动，包括 [Argon](https://en.wikipedia.org/wiki/Argon2) 和 [Argon2id](https://en.wikipedia.org/wiki/Argon2)。

你可以通过环境变量 `HASH_DRIVER` 来指定应用所用的哈希驱动。如果你希望对 Laravel 的哈希驱动进行更全面的配置，也可以使用 Artisan 命令发布完整的 `hashing` 配置文件：

```shell
php artisan config:publish hashing
```

## 基础用法



### 哈希密码

你可以通过调用 `Hash` facade 中的 `make` 方法来对密码进行加密：

```php
<?php

namespace App\Http\Controllers;

use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;

class PasswordController extends Controller
{
    /**
     * 更新用户密码。
     */
    public function update(Request $request): RedirectResponse
    {
          // 校验新密码长度...

        $request->user()->fill([
            'password' => Hash::make($request->newPassword)
        ])->save();

        return redirect('/profile');
    }
}
```

#### 调整 Bcrypt 的计算成本（工作因子）

如果你选择使用 Bcrypt 算法，可以通过 `make` 方法的 `rounds` 参数设置加密强度（即计算成本）。不过，Laravel 默认设置的工作因子已经适用于大多数场景：

```php
$hashed = Hash::make('password', [
    'rounds' => 12,
]);
```

#### 调整 Argon2 的计算成本

若你使用的是 Argon2 算法，也可以使用 `make` 方法设置加密成本参数，如 `memory`（内存使用量）、`time`（计算时间）、`threads`（线程数）。但 Laravel 默认值同样已满足大部分应用的需求：

```php
$hashed = Hash::make('password', [
    'memory' => 1024,
    'time' => 2,
    'threads' => 2,
]);
```

> 关于这些参数的详细说明，请参考 [PHP 官方 Argon 哈希文档](https://secure.php.net/manual/en/function.password-hash.php)。

### 校验密码是否匹配加密值

你可以使用 `Hash` facade 提供的 `check` 方法，来判断明文字符串是否与某个加密后的哈希值一致：

```php
if (Hash::check('plain-text', $hashedPassword)) {
    // The passwords match...
}
```




### 确定密码是否需要重新哈希

`Hash` 门面（facade）提供的 `needsRehash` 方法允许你确定自从密码被哈希后，哈希器使用的工作因子（work factor）是否发生了变化。一些应用会选择在认证过程中执行此检查：

```php
if (Hash::needsRehash($hashed)) {
    $hashed = Hash::make('plain-text');
}
```

<a name="hash-algorithm-verification"></a>
## 哈希算法验证

为防止哈希算法被篡改，Laravel 的 `Hash::check` 方法会首先验证给定的哈希是否是使用应用程序选择的哈希算法生成的。如果算法不同，将会抛出 `RuntimeException` 异常。

大多数应用不希望哈希算法发生变化，因为出现不同的算法可能表明存在恶意攻击，这是大多数应用的一种预防机制。然而，如果你需要在应用程序内支持多种哈希算法，例如在从一种算法迁移至另一种算法时，你可以通过将 `HASH_VERIFY` 环境变量设置为 `false` 来禁用哈希算法的验证：

```ini
HASH_VERIFY=false
```
