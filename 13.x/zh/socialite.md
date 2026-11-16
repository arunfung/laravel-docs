# Laravel Socialite

- [介绍](#introduction)
- [安装](#installation)
- [升级 Socialite](#upgrading-socialite)
- [配置](#configuration)
- [认证](#authentication)
    - [路由](#routing)
    - [认证与存储](#authentication-and-storage)
    - [访问权限范围](#access-scopes)
    - [Slack 机器人权限范围](#slack-bot-scopes)
    - [可选参数](#optional-parameters)
- [获取用户信息](#retrieving-user-details)
- [测试](#testing)

<a name="introduction"></a>
## 介绍

除了常见的基于表单的认证外，Laravel 还通过 [Laravel Socialite](https://github.com/laravel/socialite) 提供了一种简单、便捷的方式，使用 OAuth 提供商进行认证。Socialite 目前支持通过 Facebook、X、LinkedIn、Google、GitHub、GitLab、Bitbucket 和 Slack 进行认证。

> [!NOTE]
> 其他平台的适配器可以通过社区维护的 [Socialite Providers](https://socialiteproviders.com/) 网站获取。

<a name="installation"></a>
## 安装

要开始使用 Socialite，请使用 Composer 包管理器将其添加到项目依赖中：

```shell
composer require laravel/socialite
```

<a name="upgrading-socialite"></a>
## 升级 Socialite

升级到 Socialite 的新主版本时，请务必仔细阅读 [升级指南](https://github.com/laravel/socialite/blob/master/UPGRADE.md)。

<a name="configuration"></a>
## 配置

使用 Socialite 之前，需要添加应用所使用的 OAuth 提供商凭证。通常，可以在用于认证的服务控制面板中创建「开发者应用」来获取这些凭证。

这些凭证应放在应用的 `config/services.php` 配置文件中，并根据应用所需的提供商，使用 `facebook`、`x`、`linkedin-openid`、`google`、`github`、`gitlab`、`bitbucket`、`slack` 或 `slack-openid` 作为键：

```php
'github' => [
    'client_id' => env('GITHUB_CLIENT_ID'),
    'client_secret' => env('GITHUB_CLIENT_SECRET'),
    'redirect' => 'http://example.com/callback-url',
],
```

> [!NOTE]
> 如果 `redirect` 选项包含相对路径，它会自动解析为完整的 URL。

<a name="authentication"></a>
## 认证

<a name="routing"></a>
### 路由

要通过 OAuth 提供商认证用户，需要两个路由：一个将用户重定向到 OAuth 提供商，另一个在认证后接收提供商的回调。下面的路由示例演示了两者的实现：

```php
use Laravel\Socialite\Socialite;

Route::get('/auth/redirect', function () {
    return Socialite::driver('github')->redirect();
});

Route::get('/auth/callback', function () {
    $user = Socialite::driver('github')->user();

    // $user->token
});
```

`Socialite` 门面提供的 `redirect` 方法负责将用户重定向到 OAuth 提供商；用户批准认证请求后，`user` 方法会检查传入的请求，并从提供商获取用户信息。

<a name="authentication-and-storage"></a>
### 认证与存储

从 OAuth 提供商获取用户后，可以判断用户是否存在于应用数据库中，并 [认证该用户](/docs/{{version}}/authentication#authenticate-a-user-instance)。如果用户不存在，通常会在数据库中创建一条新记录来表示该用户：

```php
use App\Models\User;
use Illuminate\Support\Facades\Auth;
use Laravel\Socialite\Socialite;

Route::get('/auth/callback', function () {
    $githubUser = Socialite::driver('github')->user();

    $user = User::updateOrCreate([
        'github_id' => $githubUser->id,
    ], [
        'name' => $githubUser->name,
        'email' => $githubUser->email,
        'github_token' => $githubUser->token,
        'github_refresh_token' => $githubUser->refreshToken,
    ]);

    Auth::login($user);

    return redirect('/dashboard');
});
```

> [!NOTE]
> 有关特定 OAuth 提供商可提供哪些用户信息，请参阅 [获取用户信息](#retrieving-user-details) 文档。

<a name="access-scopes"></a>
### 访问权限范围

重定向用户之前，可以使用 `scopes` 方法指定认证请求中应包含的「权限范围」。该方法会将此前指定的所有权限范围与你指定的范围合并：

```php
use Laravel\Socialite\Socialite;

return Socialite::driver('github')
    ->scopes(['read:user', 'public_repo'])
    ->redirect();
```

可以使用 `setScopes` 方法覆盖认证请求中所有现有的权限范围：

```php
return Socialite::driver('github')
    ->setScopes(['read:user', 'public_repo'])
    ->redirect();
```

<a name="slack-bot-scopes"></a>
### Slack 机器人权限范围

Slack API 提供 [不同类型的访问令牌](https://api.slack.com/authentication/token-types)，每种令牌都有各自的 [权限范围](https://api.slack.com/scopes)。Socialite 兼容以下两种 Slack 访问令牌：

<div class="content-list" markdown="1">

- Bot（以 `xoxb-` 为前缀）
- User（以 `xoxp-` 为前缀）

</div>

默认情况下，`slack` 驱动会生成 `user` 令牌，调用该驱动的 `user` 方法会返回用户详细信息。

如果应用需要向其用户拥有的外部 Slack 工作区发送通知，Bot 令牌尤其有用。要生成 Bot 令牌，请在将用户重定向到 Slack 进行认证之前调用 `asBotUser` 方法：

```php
return Socialite::driver('slack')
    ->asBotUser()
    ->setScopes(['chat:write', 'chat:write.public', 'chat:write.customize'])
    ->redirect();
```

此外，Slack 在认证后将用户重定向回应用时，必须先调用 `asBotUser` 方法，再调用 `user` 方法：

```php
$user = Socialite::driver('slack')->asBotUser()->user();
```

生成 Bot 令牌时，`user` 方法仍会返回 `Laravel\Socialite\Two\User` 实例，但只有 `token` 属性会被填充。可以存储该令牌，以便 [向已认证用户的 Slack 工作区发送通知](/docs/{{version}}/notifications#notifying-external-slack-workspaces)。

<a name="optional-parameters"></a>
### 可选参数

许多 OAuth 提供商支持在重定向请求中使用其他可选参数。要在请求中包含这些参数，请使用关联数组调用 `with` 方法：

```php
use Laravel\Socialite\Socialite;

return Socialite::driver('google')
    ->with(['hd' => 'example.com'])
    ->redirect();
```

> [!WARNING]
> 使用 `with` 方法时，请注意不要传递 `state` 或 `response_type` 等保留关键字。

<a name="retrieving-user-details"></a>
## 获取用户信息

用户被重定向回应用的认证回调路由后，可以使用 Socialite 的 `user` 方法获取用户详细信息。该方法返回的用户对象提供了多种属性和方法，可用于将用户信息存储到自己的数据库中。

根据认证所用的 OAuth 提供商支持 OAuth 1.0 还是 OAuth 2.0，该对象可用的属性和方法可能有所不同：

```php
use Laravel\Socialite\Socialite;

Route::get('/auth/callback', function () {
    $user = Socialite::driver('github')->user();

    // OAuth 2.0 提供商……
    $token = $user->token;
    $refreshToken = $user->refreshToken;
    $expiresIn = $user->expiresIn;

    // OAuth 1.0 提供商……
    $token = $user->token;
    $tokenSecret = $user->tokenSecret;

    // 所有提供商……
    $user->getId();
    $user->getNickname();
    $user->getName();
    $user->getEmail();
    $user->getAvatar();
});
```

<a name="retrieving-user-details-from-a-token-oauth2"></a>
#### 从令牌获取用户信息

如果已拥有用户的有效访问令牌，可以使用 Socialite 的 `userFromToken` 方法获取该用户的详细信息：

```php
use Laravel\Socialite\Socialite;

$user = Socialite::driver('github')->userFromToken($token);
```

如果通过 iOS 应用使用 Facebook Limited Login，Facebook 会返回 OIDC 令牌，而不是访问令牌。要从 OIDC 令牌获取用户信息，请将发起登录时使用的 nonce 提供给 `userFromToken` 方法：

```php
$user = Socialite::driver('facebook')->userFromToken($token, $nonce);
```

<a name="stateless-authentication"></a>
#### 无状态认证

可以使用 `stateless` 方法禁用会话状态验证。这适用于向不使用基于 Cookie 的会话的无状态 API 添加社交认证：

```php
use Laravel\Socialite\Socialite;

return Socialite::driver('google')->stateless()->user();
```

<a name="testing"></a>
## 测试

Laravel Socialite 提供了一种便捷的方式来测试 OAuth 认证流程，无需向 OAuth 提供商发送实际请求。`fake` 方法允许你模拟 OAuth 提供商的行为，并定义应返回的用户数据。

<a name="faking-the-redirect"></a>
#### 模拟重定向

要测试应用是否正确地将用户重定向到 OAuth 提供商，可以在请求重定向路由之前调用 `fake` 方法。这样，Socialite 会返回一个指向模拟授权 URL 的重定向，而不是重定向到实际的 OAuth 提供商：

```php
use Laravel\Socialite\Socialite;

test('user is redirected to github', function () {
    Socialite::fake('github');

    $response = $this->get('/auth/github/redirect');

    $response->assertRedirect();
});
```

<a name="faking-the-callback"></a>
#### 模拟回调

要测试应用的回调路由，可以调用 `fake` 方法并提供一个 `User` 实例，供应用向提供商请求用户详细信息时返回。可以使用 `fake` 方法创建该 `User` 实例：

```php
use Laravel\Socialite\Socialite;
use Laravel\Socialite\Two\User;

test('user can login with github', function () {
    Socialite::fake('github', User::fake([
        'id' => 'github-123',
        'name' => 'Jason Beggs',
        'email' => 'jason@example.com',
    ]));

    $response = $this->get('/auth/github/callback');

    $response->assertRedirect('/dashboard');

    $this->assertDatabaseHas('users', [
        'name' => 'Jason Beggs',
        'email' => 'jason@example.com',
        'github_id' => 'github-123',
    ]);
});
```

默认情况下，`User` 实例会包含模拟的 OAuth 令牌值。如有需要，可以向 `fake` 方法传入额外属性来覆盖这些值：

```php
$fakeUser = User::fake([
    'id' => 'github-123',
    'name' => 'Jason Beggs',
    'email' => 'jason@example.com',
    'token' => 'fake-token',
    'refreshToken' => 'fake-refresh-token',
    'expiresIn' => 3600,
    'approvedScopes' => ['read', 'write'],
]);
```

可以使用 `Laravel\Socialite\One\User` 类模拟 OAuth 1 用户。
