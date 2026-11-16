
# Laravel 社交登录

-   [介绍](#introduction)
-   [安装](#installation)
-   [升级 Socialite](#upgrading-socialite)
-   [配置](#configuration)
-   [认证](#authentication)
    -   [路由](#routing)
    -   [认证与存储](#authentication-and-storage)
    -   [访问权限范围](#access-scopes)
    -   [Slack 机器人权限范围](#slack-bot-scopes)
    -   [可选参数](#optional-parameters)
-   [获取用户信息](#retrieving-user-details)

## 介绍

除了典型的基于表单的认证之外，Laravel 还提供了一种简单、便捷的方式，通过 [Laravel Socialite](https://github.com/laravel/socialite) 来使用 OAuth 提供商进行认证。Socialite 当前支持通过 Facebook、X、LinkedIn、Google、GitHub、GitLab、Bitbucket 和 Slack 进行认证。

> [!注意]
> 针对其他平台的适配器，可以通过社区驱动的 [Socialite Providers](https://socialiteproviders.com/) 网站获取。

## 安装

要开始使用 Socialite，请使用 Composer 包管理器将该包添加到项目的依赖中：

```shell
composer require laravel/socialite
```

## 升级 Socialite

在升级到 Socialite 的新主版本时，务必要仔细查看 [升级指南](https://github.com/laravel/socialite/blob/master/UPGRADE.md)。

## 配置

在使用 Socialite 之前，你需要为你的应用使用的 OAuth 提供商添加凭证。通常，这些凭证可以通过在你将要认证的服务的控制面板中创建“开发者应用”来获取。

这些凭证应该放在你应用的 `config/services.php` 配置文件中，并且根据你应用所需的提供商，使用 `facebook`、`x`、`linkedin-openid`、`google`、`github`、`gitlab`、`bitbucket`、`slack` 或 `slack-openid` 作为键，例如：

```php
'github' => [
    'client_id' => env('GITHUB_CLIENT_ID'),
    'client_secret' => env('GITHUB_CLIENT_SECRET'),
    'redirect' => 'http://example.com/callback-url',
],
```

> [!注意]
> 如果 `redirect` 选项包含相对路径，它会自动解析为完整的 URL。



## 认证

### 路由

要使用 OAuth 提供商对用户进行认证，你需要两个路由：一个用于将用户重定向到 OAuth 提供商，另一个用于在认证后接收提供商的回调。下面的示例路由演示了这两个路由的实现：

```php
use Laravel\Socialite\Facades\Socialite;

Route::get('/auth/redirect', function () {
    return Socialite::driver('github')->redirect();
});

Route::get('/auth/callback', function () {
    $user = Socialite::driver('github')->user();

    // $user->token
});
```

`Socialite` facade 提供的 `redirect` 方法会处理将用户重定向到 OAuth 提供商，而 `user` 方法会检查传入请求，并在用户批准认证请求后，从提供商获取用户信息。

### 认证与存储

一旦从 OAuth 提供商获取到用户信息，你可以判断该用户是否存在于应用的数据库中，并 [认证用户](/docs/laravel/12.x/authentication#authenticate-a-user-instance)。如果用户在应用的数据库中不存在，通常会创建一条新记录来表示该用户：

```php
use App\Models\User;
use Illuminate\Support\Facades\Auth;
use Laravel\Socialite\Facades\Socialite;

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

> [!注意]
> 关于从特定 OAuth 提供商可以获取哪些用户信息的更多内容，请参考 [获取用户信息](#retrieving-user-details) 文档。



### 访问权限范围（Access Scopes）

在重定向用户之前，你可以使用 `scopes` 方法来指定应包含在认证请求中的“权限范围”。此方法会将你之前指定的所有权限范围与新指定的权限范围合并：

```php
use Laravel\Socialite\Facades\Socialite;

return Socialite::driver('github')
    ->scopes(['read:user', 'public_repo'])
    ->redirect();
```

你也可以使用 `setScopes` 方法覆盖认证请求中所有现有的权限范围：

```php
return Socialite::driver('github')
    ->setScopes(['read:user', 'public_repo'])
    ->redirect();
```

### Slack 机器人权限范围（Slack Bot Scopes）

Slack 的 API 提供了[不同类型的访问令牌](https://api.slack.com/authentication/token-types)，每种令牌都有自己的一套[权限范围](https://api.slack.com/scopes)。Socialite 与以下两种 Slack 访问令牌类型兼容：

-   Bot（前缀为 `xoxb-`）

-   User（前缀为 `xoxp-`）

默认情况下，`slack` 驱动会生成一个 `user` 令牌，并且调用该驱动的 `user` 方法会返回用户的详细信息。

如果你的应用程序需要向用户拥有的外部 Slack 工作区发送通知，Bot 令牌将非常有用。要生成 Bot 令牌，请在将用户重定向到 Slack 进行认证之前调用 `asBotUser` 方法：

```php
return Socialite::driver('slack')
    ->asBotUser()
    ->setScopes(['chat:write', 'chat:write.public', 'chat:write.customize'])
    ->redirect();
```

此外，在 Slack 在用户认证后重定向回你的应用时，你必须在调用 `user` 方法之前调用 `asBotUser` 方法：

```php
$user = Socialite::driver('slack')->asBotUser()->user();
```



在生成 Bot 令牌时，`user` 方法仍然会返回一个 `Laravel\Socialite\Two\User` 实例；不过，只有 `token` 属性会被填充。这个令牌可以存储，以便[向已认证用户的 Slack 工作区发送通知](/docs/laravel/12.x/notifications#notifying-external-slack-workspaces)。

### 可选参数（Optional Parameters）

许多 OAuth 提供商支持在重定向请求中使用其他可选参数。要在请求中包含任何可选参数，请使用关联数组调用 `with` 方法：

```php
use Laravel\Socialite\Facades\Socialite;

return Socialite::driver('google')
    ->with(['hd' => 'example.com'])
    ->redirect();
```
> [!警告]
> 使用 `with` 方法时，请注意不要传递任何保留关键字，例如 `state` 或 `response_type`。

## 获取用户信息（Retrieving User Details）

在用户被重定向回你应用的认证回调路由后，你可以使用 Socialite 的 `user` 方法获取用户的详细信息。`user` 方法返回的用户对象提供了多种属性和方法，可用于将用户信息存储到你自己的数据库中。

根据你认证的 OAuth 提供商支持 OAuth 1.0 还是 OAuth 2.0，该对象可能具有不同的属性和方法：

```php
use Laravel\Socialite\Facades\Socialite;

Route::get('/auth/callback', function () {
    $user = Socialite::driver('github')->user();

    // OAuth 2.0 提供商...
    $token = $user->token;
    $refreshToken = $user->refreshToken;
    $expiresIn = $user->expiresIn;

    // OAuth 1.0 提供商...
    $token = $user->token;
    $tokenSecret = $user->tokenSecret;

    // 所有提供商...
    $user->getId();
    $user->getNickname();
    $user->getName();
    $user->getEmail();
    $user->getAvatar();
});
```



#### 从令牌获取用户信息（Retrieving User Details From a Token）

如果你已经拥有某个用户的有效访问令牌，可以使用 Socialite 的 `userFromToken` 方法获取该用户的详细信息：

```php
use Laravel\Socialite\Facades\Socialite;

$user = Socialite::driver('github')->userFromToken($token);
```

如果你通过 iOS 应用使用 Facebook Limited Login，Facebook 会返回一个 OIDC 令牌而不是访问令牌。像访问令牌一样，OIDC 令牌也可以提供给 `userFromToken` 方法，以获取用户详细信息。

#### 无状态认证（Stateless Authentication）

可以使用 `stateless` 方法禁用会话状态验证。当在不使用基于 Cookie 会话的无状态 API 中添加社交认证时，这非常有用：

```php
use Laravel\Socialite\Facades\Socialite;

return Socialite::driver('google')->stateless()->user();
```
