# Laravel Dusk

- [简介](#introduction)
- [安装](#installation)
    - [管理 ChromeDriver 安装](#managing-chromedriver-installations)
    - [使用其他浏览器](#using-other-browsers)
- [入门](#getting-started)
    - [生成测试](#generating-tests)
    - [每次测试后重置数据库](#resetting-the-database-after-each-test)
    - [运行测试](#running-tests)
    - [环境处理](#environment-handling)
- [浏览器基础](#browser-basics)
    - [创建浏览器](#creating-browsers)
    - [导航](#navigation)
    - [调整浏览器窗口大小](#resizing-browser-windows)
    - [浏览器宏](#browser-macros)
    - [身份验证](#authentication)
    - [Cookie](#cookies)
    - [执行 JavaScript](#executing-javascript)
    - [截图](#taking-a-screenshot)
    - [将控制台输出保存到磁盘](#storing-console-output-to-disk)
    - [将页面源码保存到磁盘](#storing-page-source-to-disk)
- [与元素交互](#interacting-with-elements)
    - [Dusk 选择器](#dusk-selectors)
    - [文本、值和属性](#text-values-and-attributes)
    - [与表单交互](#interacting-with-forms)
    - [附加文件](#attaching-files)
    - [按下按钮](#pressing-buttons)
    - [点击链接](#clicking-links)
    - [使用键盘](#using-the-keyboard)
    - [使用鼠标](#using-the-mouse)
    - [JavaScript 对话框](#javascript-dialogs)
    - [与内嵌框架交互](#interacting-with-iframes)
    - [限定选择器作用域](#scoping-selectors)
    - [等待元素](#waiting-for-elements)
    - [将元素滚动到可视范围](#scrolling-an-element-into-view)
- [可用断言](#available-assertions)
- [页面](#pages)
    - [生成页面](#generating-pages)
    - [配置页面](#configuring-pages)
    - [导航到页面](#navigating-to-pages)
    - [简写选择器](#shorthand-selectors)
    - [页面方法](#page-methods)
- [组件](#components)
    - [生成组件](#generating-components)
    - [使用组件](#using-components)
- [持续集成](#continuous-integration)
    - [Heroku CI](#running-tests-on-heroku-ci)
    - [Travis CI](#running-tests-on-travis-ci)
    - [GitHub Actions](#running-tests-on-github-actions)
    - [Chipper CI](#running-tests-on-chipper-ci)

<a name="introduction"></a>
## 简介

> [!WARNING]
> [Pest 4](https://pestphp.com/) 现已支持浏览器自动化测试，相比 Laravel Dusk，在性能和易用性方面都有显著提升。对于新项目，我们推荐使用 Pest 进行浏览器测试。

[Laravel Dusk](https://github.com/laravel/dusk) 提供了清晰易用的浏览器自动化和测试 API。默认情况下，Dusk 不要求你在本机安装 JDK 或 Selenium，而是使用独立安装的 [ChromeDriver](https://sites.google.com/chromium.org/driver)。不过，你也可以使用任何其他兼容 Selenium 的驱动。

<a name="installation"></a>
## 安装

首先，你应该安装 [Google Chrome](https://www.google.com/chrome)，并为项目添加 `laravel/dusk` Composer 依赖：

```shell
composer require laravel/dusk --dev
```

> [!WARNING]
> 如果你手动注册 Dusk 的服务提供者，**绝不要**在生产环境中注册它，否则可能导致任意用户都能以已认证身份访问你的应用。

安装 Dusk 包后，执行 `dusk:install` Artisan 命令。该命令会创建 `tests/Browser` 目录和一个 Dusk 测试示例，并安装适用于当前操作系统的 Chrome Driver 二进制文件：

```shell
php artisan dusk:install
```

接下来，在应用的 `.env` 文件中设置 `APP_URL` 环境变量。该值应与你在浏览器中访问应用时使用的 URL 一致。

> [!NOTE]
> 如果你使用 [Laravel Sail](/docs/{{version}}/sail) 管理本地开发环境，也请参阅 Sail 文档中[配置和运行 Dusk 测试](/docs/{{version}}/sail#laravel-dusk)的说明。

<a name="managing-chromedriver-installations"></a>
### 管理 ChromeDriver 安装

如果你想安装与 Laravel Dusk 的 `dusk:install` 命令所安装版本不同的 ChromeDriver，可以使用 `dusk:chrome-driver` 命令：

```shell
# 为当前操作系统安装最新版 ChromeDriver……
php artisan dusk:chrome-driver

# 为当前操作系统安装指定版本的 ChromeDriver……
php artisan dusk:chrome-driver 86

# 为所有支持的操作系统安装指定版本的 ChromeDriver……
php artisan dusk:chrome-driver --all

# 为当前操作系统安装与检测到的 Chrome / Chromium 版本匹配的 ChromeDriver……
php artisan dusk:chrome-driver --detect
```

> [!WARNING]
> Dusk 要求 `chromedriver` 二进制文件具有可执行权限。如果运行 Dusk 时遇到问题，请使用以下命令确保这些文件可执行：`chmod -R 0755 vendor/laravel/dusk/bin/`。

<a name="using-other-browsers"></a>
### 使用其他浏览器

默认情况下，Dusk 使用 Google Chrome 和独立安装的 [ChromeDriver](https://sites.google.com/chromium.org/driver) 运行浏览器测试。不过，你也可以启动自己的 Selenium 服务器，并在任意浏览器上运行测试。

首先，打开 `tests/DuskTestCase.php` 文件，这是应用的 Dusk 测试基类。你可以在该文件中移除对 `startChromeDriver` 方法的调用，阻止 Dusk 自动启动 ChromeDriver：

```php
/**
 * 为执行 Dusk 测试做准备。
 *
 * @beforeClass
 */
public static function prepare(): void
{
    // static::startChromeDriver();
}
```

接下来，你可以修改 `driver` 方法，连接到所需的 URL 和端口。此外，还可以修改传递给 WebDriver 的「期望能力」配置：

```php
use Facebook\WebDriver\Remote\RemoteWebDriver;

/**
 * 创建 RemoteWebDriver 实例。
 */
protected function driver(): RemoteWebDriver
{
    return RemoteWebDriver::create(
        'http://localhost:4444/wd/hub', DesiredCapabilities::phantomjs()
    );
}
```

<a name="getting-started"></a>
## 入门

<a name="generating-tests"></a>
### 生成测试

要生成 Dusk 测试，可以使用 `dusk:make` Artisan 命令。生成的测试会放在 `tests/Browser` 目录中：

```shell
php artisan dusk:make LoginTest
```

<a name="resetting-the-database-after-each-test"></a>
### 每次测试后重置数据库

你编写的大多数测试都会与从应用数据库读取数据的页面交互。不过，Dusk 测试绝不应使用 `RefreshDatabase` trait。该 trait 使用数据库事务，而事务无法跨 HTTP 请求生效。你可以选择使用 `DatabaseMigrations` 或 `DatabaseTruncation` trait。

<a name="reset-migrations"></a>
#### 使用数据库迁移

`DatabaseMigrations` trait 会在每次测试前运行数据库迁移。不过，每次测试都删除并重新创建数据库表，通常比截断表更慢：

```php tab=Pest
<?php

use Illuminate\Foundation\Testing\DatabaseMigrations;

pest()->use(DatabaseMigrations::class);

//
```

```php tab=PHPUnit
<?php

namespace Tests\Browser;

use Illuminate\Foundation\Testing\DatabaseMigrations;
use Laravel\Dusk\Browser;
use Tests\DuskTestCase;

class ExampleTest extends DuskTestCase
{
    use DatabaseMigrations;

    //
}
```

> [!WARNING]
> 执行 Dusk 测试时不能使用 SQLite 内存数据库。浏览器在独立进程中运行，无法访问其他进程中的内存数据库。

<a name="reset-truncation"></a>
#### 使用数据库截断

`DatabaseTruncation` trait 会在第一个测试运行时执行数据库迁移，确保数据库表已正确创建。随后的测试则只会截断数据库表，相比重新运行所有数据库迁移，速度更快：

```php tab=Pest
<?php

use Illuminate\Foundation\Testing\DatabaseTruncation;

pest()->use(DatabaseTruncation::class);

//
```

```php tab=PHPUnit
<?php

namespace Tests\Browser;

use App\Models\User;
use Illuminate\Foundation\Testing\DatabaseTruncation;
use Laravel\Dusk\Browser;
use Tests\DuskTestCase;

class ExampleTest extends DuskTestCase
{
    use DatabaseTruncation;

    //
}
```

默认情况下，该 trait 会截断除 `migrations` 表之外的所有表。如果你想自定义需要截断的表，可以在测试类中定义 `$tablesToTruncate` 属性：

> [!NOTE]
> 如果你使用 Pest，应该在基类 `DuskTestCase` 或测试文件所继承的其他类中定义这些属性或方法。

```php
/**
 * 指定需要截断的表。
 *
 * @var array
 */
protected $tablesToTruncate = ['users'];
```

你也可以在测试类中定义 `$exceptTables` 属性，指定哪些表不需要截断：

```php
/**
 * 指定不需要截断的表。
 *
 * @var array
 */
protected $exceptTables = ['users'];
```

要指定哪些数据库连接中的表需要截断，可以在测试类中定义 `$connectionsToTruncate` 属性：

```php
/**
 * 指定需要截断其表的数据库连接。
 *
 * @var array
 */
protected $connectionsToTruncate = ['mysql'];
```

如果你想在截断数据库之前或之后执行代码，可以在测试类中定义 `beforeTruncatingDatabase` 或 `afterTruncatingDatabase` 方法：

```php
/**
 * 执行数据库开始截断前的操作。
 */
protected function beforeTruncatingDatabase(): void
{
    //
}

/**
 * 执行数据库完成截断后的操作。
 */
protected function afterTruncatingDatabase(): void
{
    //
}
```

<a name="running-tests"></a>
### 运行测试

要运行浏览器测试，请执行 `dusk` Artisan 命令：

```shell
php artisan dusk
```

如果上次运行 `dusk` 命令时有测试失败，你可以使用 `dusk:fails` 命令优先重新运行失败的测试，以节省时间：

```shell
php artisan dusk:fails
```

`dusk` 命令接受 Pest / PHPUnit 测试运行器通常支持的所有参数，例如只运行指定[分组](https://docs.phpunit.de/en/10.5/annotations.html#group)中的测试：

```shell
php artisan dusk --group=foo
```

> [!NOTE]
> 如果你使用 [Laravel Sail](/docs/{{version}}/sail) 管理本地开发环境，请参阅 Sail 文档中[配置和运行 Dusk 测试](/docs/{{version}}/sail#laravel-dusk)的说明。

<a name="manually-starting-chromedriver"></a>
#### 手动启动 ChromeDriver

默认情况下，Dusk 会尝试自动启动 ChromeDriver。如果这在你的系统上无法正常工作，可以在运行 `dusk` 命令前手动启动 ChromeDriver。此时，你应该注释掉 `tests/DuskTestCase.php` 文件中的以下代码行：

```php
/**
 * 为执行 Dusk 测试做准备。
 *
 * @beforeClass
 */
public static function prepare(): void
{
    // static::startChromeDriver();
}
```

此外，如果你启动 ChromeDriver 时使用了 9515 以外的端口，应该修改同一类中的 `driver` 方法，使用正确的端口：

```php
use Facebook\WebDriver\Remote\RemoteWebDriver;

/**
 * 创建 RemoteWebDriver 实例。
 */
protected function driver(): RemoteWebDriver
{
    return RemoteWebDriver::create(
        'http://localhost:9515', DesiredCapabilities::chrome()
    );
}
```

<a name="environment-handling"></a>
### 环境处理

要让 Dusk 在运行测试时使用独立的环境文件，请在项目根目录创建 `.env.dusk.{environment}` 文件。例如，如果你将在 `local` 环境中执行 `dusk` 命令，就应该创建 `.env.dusk.local` 文件。

运行测试时，Dusk 会备份 `.env` 文件，并将 Dusk 环境文件重命名为 `.env`。测试完成后，原来的 `.env` 文件会恢复。

<a name="browser-basics"></a>
## 浏览器基础

<a name="creating-browsers"></a>
### 创建浏览器

首先，让我们编写一个测试，验证能否登录应用。生成测试后，可以修改它，使浏览器访问登录页面、输入凭据并点击「Login」按钮。要创建浏览器实例，可以在 Dusk 测试中调用 `browse` 方法：

```php tab=Pest
<?php

use App\Models\User;
use Illuminate\Foundation\Testing\DatabaseMigrations;

pest()->use(DatabaseMigrations::class);

test('basic example', function () {
    $user = User::factory()->create([
        'email' => 'taylor@laravel.com',
    ]);

    $this->browse(function (Browser $browser) use ($user) {
        $browser->visit('/login')
            ->type('email', $user->email)
            ->type('password', 'password')
            ->press('Login')
            ->assertPathIs('/home');
    });
});
```

```php tab=PHPUnit
<?php

namespace Tests\Browser;

use App\Models\User;
use Illuminate\Foundation\Testing\DatabaseMigrations;
use Laravel\Dusk\Browser;
use Tests\DuskTestCase;

class ExampleTest extends DuskTestCase
{
    use DatabaseMigrations;

    /**
     * 一个基本的浏览器测试示例。
     */
    public function test_basic_example(): void
    {
        $user = User::factory()->create([
            'email' => 'taylor@laravel.com',
        ]);

        $this->browse(function (Browser $browser) use ($user) {
            $browser->visit('/login')
                ->type('email', $user->email)
                ->type('password', 'password')
                ->press('Login')
                ->assertPathIs('/home');
        });
    }
}
```

如上例所示，`browse` 方法接收一个闭包。Dusk 会自动向闭包传入浏览器实例，它是用于与应用交互并进行断言的主要对象。

<a name="creating-multiple-browsers"></a>
#### 创建多个浏览器

有时，你需要多个浏览器才能正确执行测试。例如，测试通过 WebSocket 交互的聊天界面时，可能就需要多个浏览器。要创建多个浏览器，只需为传递给 `browse` 方法的闭包添加更多浏览器参数：

```php
$this->browse(function (Browser $first, Browser $second) {
    $first->loginAs(User::find(1))
        ->visit('/home')
        ->waitForText('Message');

    $second->loginAs(User::find(2))
        ->visit('/home')
        ->waitForText('Message')
        ->type('message', 'Hey Taylor')
        ->press('Send');

    $first->waitForText('Hey Taylor')
        ->assertSee('Jeffrey Way');
});
```

<a name="navigation"></a>
### 导航

你可以使用 `visit` 方法，访问应用中给定的 URI：

```php
$browser->visit('/login');
```

你可以使用 `visitRoute` 方法，访问[命名路由](/docs/{{version}}/routing#named-routes)：

```php
$browser->visitRoute($routeName, $parameters);
```

你可以使用 `back` 和 `forward` 方法，进行「后退」和「前进」操作：

```php
$browser->back();

$browser->forward();
```

你可以使用 `refresh` 方法刷新页面：

```php
$browser->refresh();
```

<a name="resizing-browser-windows"></a>
### 调整浏览器窗口大小

你可以使用 `resize` 方法调整浏览器窗口大小：

```php
$browser->resize(1920, 1080);
```

你可以使用 `maximize` 方法最大化浏览器窗口：

```php
$browser->maximize();
```

`fitContent` 方法会调整浏览器窗口大小，使其与页面内容的大小一致：

```php
$browser->fitContent();
```

测试失败时，Dusk 会在截图前自动调整浏览器大小以适应页面内容。你可以在测试中调用 `disableFitOnFailure` 方法，禁用该功能：

```php
$browser->disableFitOnFailure();
```

你可以使用 `move` 方法，将浏览器窗口移动到屏幕上的其他位置：

```php
$browser->move($x = 100, $y = 100);
```

<a name="browser-macros"></a>
### 浏览器宏

如果你想定义可在多个测试中复用的自定义浏览器方法，可以使用 `Browser` 类的 `macro` 方法。通常，应该在[服务提供者](/docs/{{version}}/providers)的 `boot` 方法中调用该方法：

```php
<?php

namespace App\Providers;

use Illuminate\Support\ServiceProvider;
use Laravel\Dusk\Browser;

class DuskServiceProvider extends ServiceProvider
{
    /**
     * 注册 Dusk 浏览器宏。
     */
    public function boot(): void
    {
        Browser::macro('scrollToElement', function (string $element = null) {
            $this->script("$('html, body').animate({ scrollTop: $('$element').offset().top }, 0);");

            return $this;
        });
    }
}
```

`macro` 函数的第一个参数是名称，第二个参数是闭包。当你在 `Browser` 实例上将宏作为方法调用时，就会执行这个闭包：

```php
$this->browse(function (Browser $browser) use ($user) {
    $browser->visit('/pay')
        ->scrollToElement('#credit-card-details')
        ->assertSee('Enter Credit Card Details');
});
```

<a name="authentication"></a>
### 身份验证

你经常需要测试要求身份验证的页面。使用 Dusk 的 `loginAs` 方法，可以避免在每次测试中都操作应用的登录界面。该方法接收可认证模型的主键，或一个可认证模型实例：

```php
use App\Models\User;
use Laravel\Dusk\Browser;

$this->browse(function (Browser $browser) {
    $browser->loginAs(User::find(1))
        ->visit('/home');
});
```

> [!WARNING]
> 使用 `loginAs` 方法后，用户会话会在该文件内的所有测试中保持。

<a name="cookies"></a>
### Cookie

你可以使用 `cookie` 方法获取或设置加密 Cookie 的值。默认情况下，Laravel 创建的所有 Cookie 都是加密的：

```php
$browser->cookie('name');

$browser->cookie('name', 'Taylor');
```

你可以使用 `plainCookie` 方法获取或设置未加密 Cookie 的值：

```php
$browser->plainCookie('name');

$browser->plainCookie('name', 'Taylor');
```

你可以使用 `deleteCookie` 方法删除给定的 Cookie：

```php
$browser->deleteCookie('name');
```

<a name="executing-javascript"></a>
### 执行 JavaScript

你可以使用 `script` 方法，在浏览器中执行任意 JavaScript 语句：

```php
$browser->script('document.documentElement.scrollTop = 0');

$browser->script([
    'document.body.scrollTop = 0',
    'document.documentElement.scrollTop = 0',
]);

$output = $browser->script('return window.location.pathname');
```

<a name="taking-a-screenshot"></a>
### 截图

你可以使用 `screenshot` 方法截图，并以给定的文件名保存。所有截图都会存储在 `tests/Browser/screenshots` 目录中：

```php
$browser->screenshot('filename');
```

你可以使用 `responsiveScreenshots` 方法，在不同断点尺寸下截取一组截图：

```php
$browser->responsiveScreenshots('filename');
```

你可以使用 `screenshotElement` 方法，为页面上的特定元素截图：

```php
$browser->screenshotElement('#selector', 'filename');
```

<a name="storing-console-output-to-disk"></a>
### 将控制台输出保存到磁盘

你可以使用 `storeConsoleLog` 方法，以给定的文件名将当前浏览器的控制台输出写入磁盘。控制台输出会保存在 `tests/Browser/console` 目录中：

```php
$browser->storeConsoleLog('filename');
```

<a name="storing-page-source-to-disk"></a>
### 将页面源码保存到磁盘

你可以使用 `storeSource` 方法，以给定的文件名将当前页面源码写入磁盘。页面源码会保存在 `tests/Browser/source` 目录中：

```php
$browser->storeSource('filename');
```

<a name="interacting-with-elements"></a>
## 与元素交互

<a name="dusk-selectors"></a>
### Dusk 选择器

为元素交互选择合适的 CSS 选择器，是编写 Dusk 测试时最困难的事情之一。随着时间推移，前端变化可能导致使用以下 CSS 选择器的测试失效：

```html
// HTML 示例……

<button>Login</button>
```

```php
// 测试代码……

$browser->click('.login-page .container div > button');
```

Dusk 选择器让你能够专注于编写有效的测试，而无需记住 CSS 选择器。要定义选择器，请为 HTML 元素添加 `dusk` 属性。随后在 Dusk 浏览器中交互时，为选择器加上 `@` 前缀，即可在测试中操作对应的元素：

```html
// HTML 示例……

<button dusk="login-button">Login</button>
```

```php
// 测试代码……

$browser->click('@login-button');
```

如有需要，你可以通过 `selectorHtmlAttribute` 方法，自定义 Dusk 选择器使用的 HTML 属性。通常，应该在应用 `AppServiceProvider` 的 `boot` 方法中调用该方法：

```php
use Laravel\Dusk\Dusk;

Dusk::selectorHtmlAttribute('data-dusk');
```

<a name="text-values-and-attributes"></a>
### 文本、值和属性

<a name="retrieving-setting-values"></a>
#### 获取和设置值

Dusk 提供了多个方法，用于操作页面元素的当前值、显示文本和属性。例如，要获取与给定 CSS 或 Dusk 选择器匹配的元素的「值」，可以使用 `value` 方法：

```php
// 获取值……
$value = $browser->value('selector');

// 设置值……
$browser->value('selector', 'value');
```

你可以使用 `inputValue` 方法，获取具有给定字段名称的输入元素的「值」：

```php
$value = $browser->inputValue('field');
```

<a name="retrieving-text"></a>
#### 获取文本

你可以使用 `text` 方法，获取与给定选择器匹配的元素的显示文本：

```php
$text = $browser->text('selector');
```

<a name="retrieving-attributes"></a>
#### 获取属性

最后，你可以使用 `attribute` 方法，获取与给定选择器匹配的元素的某个属性值：

```php
$attribute = $browser->attribute('selector', 'value');
```

<a name="interacting-with-forms"></a>
### 与表单交互

<a name="typing-values"></a>
#### 输入值

Dusk 提供了多种方法，用于操作表单和输入元素。首先，来看一个在输入框中输入文本的示例：

```php
$browser->type('email', 'taylor@laravel.com');
```

请注意，虽然 `type` 方法在需要时接收 CSS 选择器，但并非必须传入。如果没有提供 CSS 选择器，Dusk 会查找 `name` 属性与给定名称匹配的 `input` 或 `textarea` 字段。

要在不清空字段内容的情况下追加文本，可以使用 `append` 方法：

```php
$browser->type('tags', 'foo')
    ->append('tags', ', bar, baz');
```

你可以使用 `clear` 方法清空输入框的值：

```php
$browser->clear('email');
```

你可以使用 `typeSlowly` 方法，让 Dusk 缓慢输入。默认情况下，每次按键之间会暂停 100 毫秒。要自定义按键间隔，可以将所需的毫秒数作为第三个参数传入：

```php
$browser->typeSlowly('mobile', '+1 (202) 555-5555');

$browser->typeSlowly('mobile', '+1 (202) 555-5555', 300);
```

你可以使用 `appendSlowly` 方法缓慢追加文本：

```php
$browser->type('tags', 'foo')
    ->appendSlowly('tags', ', bar, baz');
```

<a name="dropdowns"></a>
#### 下拉列表

要选择 `select` 元素中的某个值，可以使用 `select` 方法。与 `type` 方法一样，`select` 方法不要求提供完整的 CSS 选择器。传入的值应该是选项实际的值，而非显示文本：

```php
$browser->select('size', 'Large');
```

省略第二个参数时，可以随机选择一个选项：

```php
$browser->select('size');
```

将数组作为第二个参数传递给 `select` 方法，可以选择多个选项：

```php
$browser->select('categories', ['Art', 'Music']);
```

<a name="checkboxes"></a>
#### 复选框

你可以使用 `check` 方法勾选复选框。与其他许多输入相关的方法一样，该方法不要求提供完整的 CSS 选择器。如果找不到匹配的 CSS 选择器，Dusk 会查找 `name` 属性匹配的复选框：

```php
$browser->check('terms');
```

你可以使用 `uncheck` 方法取消勾选复选框：

```php
$browser->uncheck('terms');
```

<a name="radio-buttons"></a>
#### 单选按钮

你可以使用 `radio` 方法选中 `radio` 输入选项。与其他许多输入相关的方法一样，该方法不要求提供完整的 CSS 选择器。如果找不到匹配的 CSS 选择器，Dusk 会查找 `name` 和 `value` 属性均匹配的 `radio` 输入元素：

```php
$browser->radio('size', 'large');
```

<a name="attaching-files"></a>
### 附加文件

你可以使用 `attach` 方法，为 `file` 输入元素附加文件。与其他许多输入相关的方法一样，该方法不要求提供完整的 CSS 选择器。如果找不到匹配的 CSS 选择器，Dusk 会查找 `name` 属性匹配的 `file` 输入元素：

```php
$browser->attach('photo', __DIR__.'/photos/mountains.png');
```

> [!WARNING]
> `attach` 函数要求服务器已安装并启用 PHP 的 `Zip` 扩展。

<a name="pressing-buttons"></a>
### 按下按钮

你可以使用 `press` 方法点击页面上的按钮元素。传入的参数可以是按钮的显示文本，也可以是 CSS / Dusk 选择器：

```php
$browser->press('Login');
```

提交表单时，许多应用会在提交按钮被点击后禁用它，并在提交表单的 HTTP 请求完成后重新启用。要点击按钮并等待它重新启用，可以使用 `pressAndWaitFor` 方法：

```php
// 点击按钮，最多等待 5 秒，直到它重新启用……
$browser->pressAndWaitFor('Save');

// 点击按钮，最多等待 1 秒，直到它重新启用……
$browser->pressAndWaitFor('Save', 1);
```

<a name="clicking-links"></a>
### 点击链接

你可以使用浏览器实例的 `clickLink` 方法点击链接。该方法会点击具有给定显示文本的链接：

```php
$browser->clickLink($linkText);
```

你可以使用 `seeLink` 方法，判断页面上是否有具有给定显示文本的可见链接：

```php
if ($browser->seeLink($linkText)) {
    // ...
}
```

> [!WARNING]
> 这些方法依赖 jQuery。如果页面中没有 jQuery，Dusk 会自动将其注入页面，以便在测试期间使用。

<a name="using-the-keyboard"></a>
### 使用键盘

相比 `type` 方法，`keys` 方法允许你向给定元素发送更复杂的输入序列。例如，可以让 Dusk 在输入值时按住修饰键。下例中，向匹配给定选择器的元素输入 `taylor` 时会按住 `shift` 键；输入完成后，再不带任何修饰键地输入 `swift`：

```php
$browser->keys('selector', ['{shift}', 'taylor'], 'swift');
```

`keys` 方法的另一个实用场景，是向应用的主 CSS 选择器发送「键盘快捷键」组合：

```php
$browser->keys('.app', ['{command}', 'j']);
```

> [!NOTE]
> 所有修饰键（如 `{command}`）都用 `{}` 字符包裹，并对应于 `Facebook\WebDriver\WebDriverKeys` 类中定义的常量。你可以在 [GitHub 上查看](https://github.com/php-webdriver/php-webdriver/blob/master/lib/WebDriverKeys.php)这些常量。

<a name="fluent-keyboard-interactions"></a>
#### 链式键盘交互

Dusk 还提供了 `withKeyboard` 方法，让你通过 `Laravel\Dusk\Keyboard` 类，以链式调用执行复杂的键盘交互。`Keyboard` 类提供了 `press`、`release`、`type` 和 `pause` 方法：

```php
use Laravel\Dusk\Keyboard;

$browser->withKeyboard(function (Keyboard $keyboard) {
    $keyboard->press('c')
        ->pause(1000)
        ->release('c')
        ->type(['c', 'e', 'o']);
});
```

<a name="keyboard-macros"></a>
#### 键盘宏

如果你想定义可在整个测试套件中轻松复用的自定义键盘交互，可以使用 `Keyboard` 类提供的 `macro` 方法。通常，应该在[服务提供者](/docs/{{version}}/providers)的 `boot` 方法中调用该方法：

```php
<?php

namespace App\Providers;

use Facebook\WebDriver\WebDriverKeys;
use Illuminate\Support\ServiceProvider;
use Laravel\Dusk\Keyboard;
use Laravel\Dusk\OperatingSystem;

class DuskServiceProvider extends ServiceProvider
{
    /**
     * 注册 Dusk 浏览器宏。
     */
    public function boot(): void
    {
        Keyboard::macro('copy', function (string $element = null) {
            $this->type([
                OperatingSystem::onMac() ? WebDriverKeys::META : WebDriverKeys::CONTROL, 'c',
            ]);

            return $this;
        });

        Keyboard::macro('paste', function (string $element = null) {
            $this->type([
                OperatingSystem::onMac() ? WebDriverKeys::META : WebDriverKeys::CONTROL, 'v',
            ]);

            return $this;
        });
    }
}
```

`macro` 函数的第一个参数是名称，第二个参数是闭包。当你在 `Keyboard` 实例上将宏作为方法调用时，就会执行这个闭包：

```php
$browser->click('@textarea')
    ->withKeyboard(fn (Keyboard $keyboard) => $keyboard->copy())
    ->click('@another-textarea')
    ->withKeyboard(fn (Keyboard $keyboard) => $keyboard->paste());
```

<a name="using-the-mouse"></a>
### 使用鼠标

<a name="clicking-on-elements"></a>
#### 点击元素

你可以使用 `click` 方法，点击与给定 CSS 或 Dusk 选择器匹配的元素：

```php
$browser->click('.selector');
```

你可以使用 `clickAtXPath` 方法，点击与给定 XPath 表达式匹配的元素：

```php
$browser->clickAtXPath('//div[@class = "selector"]');
```

你可以使用 `clickAtPoint` 方法，点击浏览器可视区域内给定坐标处最上层的元素：

```php
$browser->clickAtPoint($x = 0, $y = 0);
```

你可以使用 `doubleClick` 方法模拟鼠标双击：

```php
$browser->doubleClick();

$browser->doubleClick('.selector');
```

你可以使用 `rightClick` 方法模拟鼠标右键点击：

```php
$browser->rightClick();

$browser->rightClick('.selector');
```

你可以使用 `clickAndHold` 方法模拟按住鼠标按钮。随后调用 `releaseMouse` 方法，即可结束该操作并释放鼠标按钮：

```php
$browser->clickAndHold('.selector');

$browser->clickAndHold()
    ->pause(1000)
    ->releaseMouse();
```

你可以使用 `controlClick` 方法，模拟浏览器中的 `ctrl+click` 事件：

```php
$browser->controlClick();

$browser->controlClick('.selector');
```

你可以使用 `clickWhenVisible` 或 `clickWhenEnabled` 方法，等待元素准备就绪后只点击一次：

```php
$browser->clickWhenVisible('@save-button');
$browser->clickWhenEnabled('@submit-button');
```

<a name="mouseover"></a>
#### 鼠标悬停

需要将鼠标移到与给定 CSS 或 Dusk 选择器匹配的元素上时，可以使用 `mouseover` 方法：

```php
$browser->mouseover('.selector');
```

<a name="drag-drop"></a>
#### 拖放

你可以使用 `drag` 方法，将与给定选择器匹配的元素拖动到另一个元素：

```php
$browser->drag('.from-selector', '.to-selector');
```

你也可以沿单一方向拖动元素：

```php
$browser->dragLeft('.selector', $pixels = 10);
$browser->dragRight('.selector', $pixels = 10);
$browser->dragUp('.selector', $pixels = 10);
$browser->dragDown('.selector', $pixels = 10);
```

最后，你还可以按给定的偏移量拖动元素：

```php
$browser->dragOffset('.selector', $x = 10, $y = 10);
```

<a name="javascript-dialogs"></a>
### JavaScript 对话框

Dusk 提供了多种方法，用于与 JavaScript 对话框交互。例如，可以使用 `waitForDialog` 方法等待 JavaScript 对话框出现。该方法接收一个可选参数，指定等待对话框出现的秒数：

```php
$browser->waitForDialog($seconds = null);
```

你可以使用 `assertDialogOpened` 方法，断言对话框已显示且包含给定的消息：

```php
$browser->assertDialogOpened('Dialog message');
```

如果 JavaScript 对话框包含输入提示，可以使用 `typeInDialog` 方法在其中输入值：

```php
$browser->typeInDialog('Hello World');
```

要通过点击「确定」按钮关闭已打开的 JavaScript 对话框，可以调用 `acceptDialog` 方法：

```php
$browser->acceptDialog();
```

要通过点击「取消」按钮关闭已打开的 JavaScript 对话框，可以调用 `dismissDialog` 方法：

```php
$browser->dismissDialog();
```

<a name="interacting-with-iframes"></a>
### 与内嵌框架交互

如果你需要与 iframe 中的元素交互，可以使用 `withinFrame` 方法。传入闭包中的所有元素交互，都会限定在指定 iframe 的上下文中：

```php
$browser->withinFrame('#credit-card-details', function ($browser) {
    $browser->type('input[name="cardnumber"]', '4242424242424242')
        ->type('input[name="exp-date"]', '1224')
        ->type('input[name="cvc"]', '123')
        ->press('Pay');
});
```

<a name="scoping-selectors"></a>
### 限定选择器作用域

有时，你可能希望在给定选择器的范围内执行多项操作。例如，断言某些文本在表格内存在，然后点击该表格中的按钮。你可以使用 `with` 方法实现这一点。传入闭包中的所有操作，都会限定在原始选择器的范围内：

```php
$browser->with('.table', function (Browser $table) {
    $table->assertSee('Hello World')
        ->clickLink('Delete');
});
```

有时，你可能需要在当前作用域之外执行断言。此时可以使用 `elsewhere` 和 `elsewhereWhenAvailable` 方法：

```php
$browser->with('.table', function (Browser $table) {
    // 当前作用域为 `body .table`……

    $browser->elsewhere('.page-title', function (Browser $title) {
        // 当前作用域为 `body .page-title`……
        $title->assertSee('Hello World');
    });

    $browser->elsewhereWhenAvailable('.page-title', function (Browser $title) {
        // 当前作用域为 `body .page-title`……
        $title->assertSee('Hello World');
    });
});
```

<a name="waiting-for-elements"></a>
### 等待元素

测试大量使用 JavaScript 的应用时，通常需要等待某些元素或数据就绪后，才能继续执行测试。Dusk 让这变得很简单。你可以通过多种方法，等待页面上的元素变为可见，甚至等待给定 JavaScript 表达式的结果变为 `true`。

<a name="waiting"></a>
#### 等待

如果只需暂停测试指定的毫秒数，可以使用 `pause` 方法：

```php
$browser->pause(1000);
```

如果只想在给定条件为 `true` 时暂停测试，可以使用 `pauseIf` 方法：

```php
$browser->pauseIf(App::environment('production'), 1000);
```

同样，如果想在给定条件不为 `true` 时暂停测试，可以使用 `pauseUnless` 方法：

```php
$browser->pauseUnless(App::environment('testing'), 1000);
```

<a name="waiting-for-selectors"></a>
#### 等待选择器

你可以使用 `waitFor` 方法暂停测试，直到与给定 CSS 或 Dusk 选择器匹配的元素显示在页面上。默认最多等待五秒，超时后抛出异常。如有需要，可以将自定义超时值作为第二个参数传入：

```php
// 最多等待五秒，直到匹配的元素显示……
$browser->waitFor('.selector');

// 最多等待一秒，直到匹配的元素显示……
$browser->waitFor('.selector', 1);
```

你也可以等待与给定选择器匹配的元素包含给定文本：

```php
// 最多等待五秒，直到匹配的元素包含给定文本……
$browser->waitForTextIn('.selector', 'Hello World');

// 最多等待一秒，直到匹配的元素包含给定文本……
$browser->waitForTextIn('.selector', 'Hello World', 1);
```

你也可以等待与给定选择器匹配的元素从页面中消失：

```php
// 最多等待五秒，直到匹配的元素消失……
$browser->waitUntilMissing('.selector');

// 最多等待一秒，直到匹配的元素消失……
$browser->waitUntilMissing('.selector', 1);
```

或者，你可以等待与给定选择器匹配的元素启用或禁用：

```php
// 最多等待五秒，直到匹配的元素启用……
$browser->waitUntilEnabled('.selector');

// 最多等待一秒，直到匹配的元素启用……
$browser->waitUntilEnabled('.selector', 1);

// 最多等待五秒，直到匹配的元素禁用……
$browser->waitUntilDisabled('.selector');

// 最多等待一秒，直到匹配的元素禁用……
$browser->waitUntilDisabled('.selector', 1);
```

<a name="scoping-selectors-when-available"></a>
#### 元素就绪后限定选择器作用域

有时，你可能想先等待与给定选择器匹配的元素出现，再与其交互。例如，等待模态窗口就绪后，点击其中的「确定」按钮。你可以使用 `whenAvailable` 方法实现这一点。传入闭包中的所有元素操作，都会限定在原始选择器的范围内：

```php
$browser->whenAvailable('.modal', function (Browser $modal) {
    $modal->assertSee('Hello World')
        ->press('OK');
});
```

<a name="waiting-for-text"></a>
#### 等待文本

你可以使用 `waitForText` 方法，等待给定文本显示在页面上：

```php
// 最多等待五秒，直到文本显示……
$browser->waitForText('Hello World');

// 最多等待一秒，直到文本显示……
$browser->waitForText('Hello World', 1);
```

你可以使用 `waitUntilMissingText` 方法，等待已显示的文本从页面中移除：

```php
// 最多等待五秒，直到文本移除……
$browser->waitUntilMissingText('Hello World');

// 最多等待一秒，直到文本移除……
$browser->waitUntilMissingText('Hello World', 1);
```

<a name="waiting-for-links"></a>
#### 等待链接

你可以使用 `waitForLink` 方法，等待给定的链接文本显示在页面上：

```php
// 最多等待五秒，直到链接显示……
$browser->waitForLink('Create');

// 最多等待一秒，直到链接显示……
$browser->waitForLink('Create', 1);
```

<a name="waiting-for-inputs"></a>
#### 等待输入框

你可以使用 `waitForInput` 方法，等待给定输入框在页面上变为可见：

```php
// 最多等待五秒，直到输入框可见……
$browser->waitForInput($field);

// 最多等待一秒，直到输入框可见……
$browser->waitForInput($field, 1);
```

<a name="waiting-on-the-page-location"></a>
#### 等待页面地址

执行 `$browser->assertPathIs('/home')` 这样的路径断言时，如果 `window.location.pathname` 正在异步更新，断言可能会失败。你可以使用 `waitForLocation` 方法，等待地址变为给定值：

```php
$browser->waitForLocation('/secret');
```

`waitForLocation` 方法也可用于等待当前窗口地址变为完整的 URL：

```php
$browser->waitForLocation('https://example.com/path');
```

你也可以等待[命名路由](/docs/{{version}}/routing#named-routes)对应的地址：

```php
$browser->waitForRoute($routeName, $parameters);
```

<a name="waiting-for-page-reloads"></a>
#### 等待页面重新加载

如果你需要在执行某项操作后等待页面重新加载，可以使用 `waitForReload` 方法：

```php
use Laravel\Dusk\Browser;

$browser->waitForReload(function (Browser $browser) {
    $browser->press('Submit');
})
->assertSee('Success!');
```

等待页面重新加载通常发生在点击按钮之后，因此你可以使用更便捷的 `clickAndWaitForReload` 方法：

```php
$browser->clickAndWaitForReload('.selector')
    ->assertSee('something');
```

<a name="waiting-on-javascript-expressions"></a>
#### 等待 JavaScript 表达式

有时，你可能想暂停测试，直到给定 JavaScript 表达式的结果为 `true`。使用 `waitUntil` 方法即可轻松实现。向该方法传入表达式时，无需包含 `return` 关键字或末尾的分号：

```php
// 最多等待五秒，直到表达式的结果为 true……
$browser->waitUntil('App.data.servers.length > 0');

// 最多等待一秒，直到表达式的结果为 true……
$browser->waitUntil('App.data.servers.length > 0', 1);
```

<a name="waiting-on-vue-expressions"></a>
#### 等待 Vue 表达式

你可以使用 `waitUntilVue` 和 `waitUntilVueIsNot` 方法，分别等待 [Vue 组件](https://vuejs.org)的某个属性等于或不等于给定值：

```php
// 等待组件属性包含给定值……
$browser->waitUntilVue('user.name', 'Taylor', '@user');

// 等待组件属性不包含给定值……
$browser->waitUntilVueIsNot('user.name', null, '@user');
```

<a name="waiting-for-javascript-events"></a>
#### 等待 JavaScript 事件

你可以使用 `waitForEvent` 方法暂停测试，直到 JavaScript 事件发生：

```php
$browser->waitForEvent('load');
```

事件监听器会附加到当前作用域，默认为 `body` 元素。使用限定作用域的选择器时，事件监听器会附加到匹配的元素：

```php
$browser->with('iframe', function (Browser $iframe) {
    // 等待 iframe 的 load 事件……
    $iframe->waitForEvent('load');
});
```

你也可以将选择器作为第二个参数传递给 `waitForEvent` 方法，将事件监听器附加到特定元素：

```php
$browser->waitForEvent('load', '.selector');
```

你也可以等待 `document` 和 `window` 对象上的事件：

```php
// 等待文档滚动……
$browser->waitForEvent('scroll', 'document');

// 最多等待五秒，直到窗口大小发生变化……
$browser->waitForEvent('resize', 'window', 5);
```

<a name="waiting-with-a-callback"></a>
#### 使用回调等待

Dusk 的许多「等待」方法依赖底层的 `waitUsing` 方法。你可以直接使用该方法，等待给定闭包返回 `true`。`waitUsing` 方法接收最大等待秒数、闭包执行的间隔、闭包本身，以及可选的失败消息：

```php
$browser->waitUsing(10, 1, function () use ($something) {
    return $something->isReady();
}, "Something wasn't ready in time.");
```

<a name="scrolling-an-element-into-view"></a>
### 将元素滚动到可视范围

有时，你无法点击某个元素，是因为它位于浏览器的可视区域之外。`scrollIntoView` 方法会滚动浏览器窗口，直到给定选择器对应的元素进入可视区域：

```php
$browser->scrollIntoView('.selector')
    ->click('.selector');
```

<a name="available-assertions"></a>
## 可用断言

Dusk 提供了多种用于测试应用的断言。所有可用断言如下所列：

<style>
    .collection-method-list > p {
        columns: 10.8em 3; -moz-columns: 10.8em 3; -webkit-columns: 10.8em 3;
    }

    .collection-method-list a {
        display: block;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
</style>

<div class="collection-method-list" markdown="1">

[assertTitle](#assert-title)
[assertTitleContains](#assert-title-contains)
[assertUrlIs](#assert-url-is)
[assertSchemeIs](#assert-scheme-is)
[assertSchemeIsNot](#assert-scheme-is-not)
[assertHostIs](#assert-host-is)
[assertHostIsNot](#assert-host-is-not)
[assertPortIs](#assert-port-is)
[assertPortIsNot](#assert-port-is-not)
[assertPathBeginsWith](#assert-path-begins-with)
[assertPathEndsWith](#assert-path-ends-with)
[assertPathContains](#assert-path-contains)
[assertPathIs](#assert-path-is)
[assertPathIsNot](#assert-path-is-not)
[assertRouteIs](#assert-route-is)
[assertQueryStringHas](#assert-query-string-has)
[assertQueryStringMissing](#assert-query-string-missing)
[assertFragmentIs](#assert-fragment-is)
[assertFragmentBeginsWith](#assert-fragment-begins-with)
[assertFragmentIsNot](#assert-fragment-is-not)
[assertHasCookie](#assert-has-cookie)
[assertHasPlainCookie](#assert-has-plain-cookie)
[assertCookieMissing](#assert-cookie-missing)
[assertPlainCookieMissing](#assert-plain-cookie-missing)
[assertCookieValue](#assert-cookie-value)
[assertPlainCookieValue](#assert-plain-cookie-value)
[assertSee](#assert-see)
[assertDontSee](#assert-dont-see)
[assertSeeIn](#assert-see-in)
[assertDontSeeIn](#assert-dont-see-in)
[assertSeeAnythingIn](#assert-see-anything-in)
[assertSeeNothingIn](#assert-see-nothing-in)
[assertCount](#assert-count)
[assertScript](#assert-script)
[assertSourceHas](#assert-source-has)
[assertSourceMissing](#assert-source-missing)
[assertSeeLink](#assert-see-link)
[assertDontSeeLink](#assert-dont-see-link)
[assertInputValue](#assert-input-value)
[assertInputValueIsNot](#assert-input-value-is-not)
[assertChecked](#assert-checked)
[assertNotChecked](#assert-not-checked)
[assertIndeterminate](#assert-indeterminate)
[assertRadioSelected](#assert-radio-selected)
[assertRadioNotSelected](#assert-radio-not-selected)
[assertSelected](#assert-selected)
[assertNotSelected](#assert-not-selected)
[assertSelectHasOptions](#assert-select-has-options)
[assertSelectMissingOptions](#assert-select-missing-options)
[assertSelectHasOption](#assert-select-has-option)
[assertSelectMissingOption](#assert-select-missing-option)
[assertValue](#assert-value)
[assertValueIsNot](#assert-value-is-not)
[assertAttribute](#assert-attribute)
[assertAttributeMissing](#assert-attribute-missing)
[assertAttributeContains](#assert-attribute-contains)
[assertAttributeDoesntContain](#assert-attribute-doesnt-contain)
[assertAriaAttribute](#assert-aria-attribute)
[assertDataAttribute](#assert-data-attribute)
[assertVisible](#assert-visible)
[assertPresent](#assert-present)
[assertNotPresent](#assert-not-present)
[assertMissing](#assert-missing)
[assertInputPresent](#assert-input-present)
[assertInputMissing](#assert-input-missing)
[assertDialogOpened](#assert-dialog-opened)
[assertEnabled](#assert-enabled)
[assertDisabled](#assert-disabled)
[assertButtonEnabled](#assert-button-enabled)
[assertButtonDisabled](#assert-button-disabled)
[assertFocused](#assert-focused)
[assertNotFocused](#assert-not-focused)
[assertAuthenticated](#assert-authenticated)
[assertGuest](#assert-guest)
[assertAuthenticatedAs](#assert-authenticated-as)
[assertVue](#assert-vue)
[assertVueIsNot](#assert-vue-is-not)
[assertVueContains](#assert-vue-contains)
[assertVueDoesntContain](#assert-vue-doesnt-contain)

</div>

<a name="assert-title"></a>
#### assertTitle

断言页面标题与给定文本匹配：

```php
$browser->assertTitle($title);
```

<a name="assert-title-contains"></a>
#### assertTitleContains

断言页面标题包含给定文本：

```php
$browser->assertTitleContains($title);
```

<a name="assert-url-is"></a>
#### assertUrlIs

断言当前 URL（不含查询字符串）与给定字符串匹配：

```php
$browser->assertUrlIs($url);
```

<a name="assert-scheme-is"></a>
#### assertSchemeIs

断言当前 URL 的协议与给定协议匹配：

```php
$browser->assertSchemeIs($scheme);
```

<a name="assert-scheme-is-not"></a>
#### assertSchemeIsNot

断言当前 URL 的协议与给定协议不匹配：

```php
$browser->assertSchemeIsNot($scheme);
```

<a name="assert-host-is"></a>
#### assertHostIs

断言当前 URL 的主机与给定主机匹配：

```php
$browser->assertHostIs($host);
```

<a name="assert-host-is-not"></a>
#### assertHostIsNot

断言当前 URL 的主机与给定主机不匹配：

```php
$browser->assertHostIsNot($host);
```

<a name="assert-port-is"></a>
#### assertPortIs

断言当前 URL 的端口与给定端口匹配：

```php
$browser->assertPortIs($port);
```

<a name="assert-port-is-not"></a>
#### assertPortIsNot

断言当前 URL 的端口与给定端口不匹配：

```php
$browser->assertPortIsNot($port);
```

<a name="assert-path-begins-with"></a>
#### assertPathBeginsWith

断言当前 URL 路径以给定路径开头：

```php
$browser->assertPathBeginsWith('/home');
```

<a name="assert-path-ends-with"></a>
#### assertPathEndsWith

断言当前 URL 路径以给定路径结尾：

```php
$browser->assertPathEndsWith('/home');
```

<a name="assert-path-contains"></a>
#### assertPathContains

断言当前 URL 路径包含给定路径：

```php
$browser->assertPathContains('/home');
```

<a name="assert-path-is"></a>
#### assertPathIs

断言当前路径与给定路径匹配：

```php
$browser->assertPathIs('/home');
```

<a name="assert-path-is-not"></a>
#### assertPathIsNot

断言当前路径与给定路径不匹配：

```php
$browser->assertPathIsNot('/home');
```

<a name="assert-route-is"></a>
#### assertRouteIs

断言当前 URL 与给定[命名路由](/docs/{{version}}/routing#named-routes)的 URL 匹配：

```php
$browser->assertRouteIs($name, $parameters);
```

<a name="assert-query-string-has"></a>
#### assertQueryStringHas

断言给定的查询字符串参数存在：

```php
$browser->assertQueryStringHas($name);
```

断言给定的查询字符串参数存在且具有给定值：

```php
$browser->assertQueryStringHas($name, $value);
```

<a name="assert-query-string-missing"></a>
#### assertQueryStringMissing

断言给定的查询字符串参数不存在：

```php
$browser->assertQueryStringMissing($name);
```

<a name="assert-fragment-is"></a>
#### assertFragmentIs

断言 URL 当前的哈希片段与给定片段匹配：

```php
$browser->assertFragmentIs('anchor');
```

<a name="assert-fragment-begins-with"></a>
#### assertFragmentBeginsWith

断言 URL 当前的哈希片段以给定片段开头：

```php
$browser->assertFragmentBeginsWith('anchor');
```

<a name="assert-fragment-is-not"></a>
#### assertFragmentIsNot

断言 URL 当前的哈希片段与给定片段不匹配：

```php
$browser->assertFragmentIsNot('anchor');
```

<a name="assert-has-cookie"></a>
#### assertHasCookie

断言给定的加密 Cookie 存在：

```php
$browser->assertHasCookie($name);
```

<a name="assert-has-plain-cookie"></a>
#### assertHasPlainCookie

断言给定的未加密 Cookie 存在：

```php
$browser->assertHasPlainCookie($name);
```

<a name="assert-cookie-missing"></a>
#### assertCookieMissing

断言给定的加密 Cookie 不存在：

```php
$browser->assertCookieMissing($name);
```

<a name="assert-plain-cookie-missing"></a>
#### assertPlainCookieMissing

断言给定的未加密 Cookie 不存在：

```php
$browser->assertPlainCookieMissing($name);
```

<a name="assert-cookie-value"></a>
#### assertCookieValue

断言加密 Cookie 具有给定值：

```php
$browser->assertCookieValue($name, $value);
```

<a name="assert-plain-cookie-value"></a>
#### assertPlainCookieValue

断言未加密 Cookie 具有给定值：

```php
$browser->assertPlainCookieValue($name, $value);
```

<a name="assert-see"></a>
#### assertSee

断言页面上存在给定文本：

```php
$browser->assertSee($text);
```

<a name="assert-dont-see"></a>
#### assertDontSee

断言页面上不存在给定文本：

```php
$browser->assertDontSee($text);
```

<a name="assert-see-in"></a>
#### assertSeeIn

断言给定选择器的范围内存在给定文本：

```php
$browser->assertSeeIn($selector, $text);
```

<a name="assert-dont-see-in"></a>
#### assertDontSeeIn

断言给定选择器的范围内不存在给定文本：

```php
$browser->assertDontSeeIn($selector, $text);
```

<a name="assert-see-anything-in"></a>
#### assertSeeAnythingIn

断言给定选择器的范围内存在任意文本：

```php
$browser->assertSeeAnythingIn($selector);
```

<a name="assert-see-nothing-in"></a>
#### assertSeeNothingIn

断言给定选择器的范围内不存在任何文本：

```php
$browser->assertSeeNothingIn($selector);
```

<a name="assert-count"></a>
#### assertCount

断言与给定选择器匹配的元素出现了指定次数：

```php
$browser->assertCount($selector, $count);
```

<a name="assert-script"></a>
#### assertScript

断言给定 JavaScript 表达式的结果等于给定值：

```php
$browser->assertScript('window.isLoaded')
    ->assertScript('document.readyState', 'complete');
```

<a name="assert-source-has"></a>
#### assertSourceHas

断言页面源码中存在给定代码：

```php
$browser->assertSourceHas($code);
```

<a name="assert-source-missing"></a>
#### assertSourceMissing

断言页面源码中不存在给定代码：

```php
$browser->assertSourceMissing($code);
```

<a name="assert-see-link"></a>
#### assertSeeLink

断言页面上存在给定链接：

```php
$browser->assertSeeLink($linkText);
```

<a name="assert-dont-see-link"></a>
#### assertDontSeeLink

断言页面上不存在给定链接：

```php
$browser->assertDontSeeLink($linkText);
```

<a name="assert-input-value"></a>
#### assertInputValue

断言给定输入字段具有给定值：

```php
$browser->assertInputValue($field, $value);
```

<a name="assert-input-value-is-not"></a>
#### assertInputValueIsNot

断言给定输入字段的值不等于给定值：

```php
$browser->assertInputValueIsNot($field, $value);
```

<a name="assert-checked"></a>
#### assertChecked

断言给定复选框已勾选：

```php
$browser->assertChecked($field);
```

<a name="assert-not-checked"></a>
#### assertNotChecked

断言给定复选框未勾选：

```php
$browser->assertNotChecked($field);
```

<a name="assert-indeterminate"></a>
#### assertIndeterminate

断言给定复选框处于不确定状态：

```php
$browser->assertIndeterminate($field);
```

<a name="assert-radio-selected"></a>
#### assertRadioSelected

断言给定单选字段已选中：

```php
$browser->assertRadioSelected($field, $value);
```

<a name="assert-radio-not-selected"></a>
#### assertRadioNotSelected

断言给定单选字段未选中：

```php
$browser->assertRadioNotSelected($field, $value);
```

<a name="assert-selected"></a>
#### assertSelected

断言给定下拉列表已选中给定值：

```php
$browser->assertSelected($field, $value);
```

<a name="assert-not-selected"></a>
#### assertNotSelected

断言给定下拉列表未选中给定值：

```php
$browser->assertNotSelected($field, $value);
```

<a name="assert-select-has-options"></a>
#### assertSelectHasOptions

断言给定值数组中的所有值都可供选择：

```php
$browser->assertSelectHasOptions($field, $values);
```

<a name="assert-select-missing-options"></a>
#### assertSelectMissingOptions

断言给定值数组中的所有值都不可供选择：

```php
$browser->assertSelectMissingOptions($field, $values);
```

<a name="assert-select-has-option"></a>
#### assertSelectHasOption

断言给定字段中存在可供选择的给定值：

```php
$browser->assertSelectHasOption($field, $value);
```

<a name="assert-select-missing-option"></a>
#### assertSelectMissingOption

断言给定值不可供选择：

```php
$browser->assertSelectMissingOption($field, $value);
```

<a name="assert-value"></a>
#### assertValue

断言与给定选择器匹配的元素具有给定值：

```php
$browser->assertValue($selector, $value);
```

<a name="assert-value-is-not"></a>
#### assertValueIsNot

断言与给定选择器匹配的元素的值不等于给定值：

```php
$browser->assertValueIsNot($selector, $value);
```

<a name="assert-attribute"></a>
#### assertAttribute

断言与给定选择器匹配的元素，其指定属性具有给定值：

```php
$browser->assertAttribute($selector, $attribute, $value);
```

<a name="assert-attribute-missing"></a>
#### assertAttributeMissing

断言与给定选择器匹配的元素不存在指定属性：

```php
$browser->assertAttributeMissing($selector, $attribute);
```

<a name="assert-attribute-contains"></a>
#### assertAttributeContains

断言与给定选择器匹配的元素，其指定属性包含给定值：

```php
$browser->assertAttributeContains($selector, $attribute, $value);
```

<a name="assert-attribute-doesnt-contain"></a>
#### assertAttributeDoesntContain

断言与给定选择器匹配的元素，其指定属性不包含给定值：

```php
$browser->assertAttributeDoesntContain($selector, $attribute, $value);
```

<a name="assert-aria-attribute"></a>
#### assertAriaAttribute

断言与给定选择器匹配的元素，其指定的 aria 属性具有给定值：

```php
$browser->assertAriaAttribute($selector, $attribute, $value);
```

例如，对于标记 `<button aria-label="Add"></button>`，你可以像下面这样对 `aria-label` 属性进行断言：

```php
$browser->assertAriaAttribute('button', 'label', 'Add');
```

<a name="assert-data-attribute"></a>
#### assertDataAttribute

断言与给定选择器匹配的元素，其指定的 data 属性具有给定值：

```php
$browser->assertDataAttribute($selector, $attribute, $value);
```

例如，对于标记 `<tr id="row-1" data-content="attendees"></tr>`，你可以像下面这样对 `data-content` 属性进行断言：

```php
$browser->assertDataAttribute('#row-1', 'content', 'attendees');
```

<a name="assert-visible"></a>
#### assertVisible

断言与给定选择器匹配的元素可见：

```php
$browser->assertVisible($selector);
```

<a name="assert-present"></a>
#### assertPresent

断言页面源码中存在与给定选择器匹配的元素：

```php
$browser->assertPresent($selector);
```

<a name="assert-not-present"></a>
#### assertNotPresent

断言页面源码中不存在与给定选择器匹配的元素：

```php
$browser->assertNotPresent($selector);
```

<a name="assert-missing"></a>
#### assertMissing

断言与给定选择器匹配的元素不可见：

```php
$browser->assertMissing($selector);
```

<a name="assert-input-present"></a>
#### assertInputPresent

断言具有给定名称的输入元素存在：

```php
$browser->assertInputPresent($name);
```

<a name="assert-input-missing"></a>
#### assertInputMissing

断言页面源码中不存在具有给定名称的输入元素：

```php
$browser->assertInputMissing($name);
```

<a name="assert-dialog-opened"></a>
#### assertDialogOpened

断言包含给定消息的 JavaScript 对话框已打开：

```php
$browser->assertDialogOpened($message);
```

<a name="assert-enabled"></a>
#### assertEnabled

断言给定字段已启用：

```php
$browser->assertEnabled($field);
```

<a name="assert-disabled"></a>
#### assertDisabled

断言给定字段已禁用：

```php
$browser->assertDisabled($field);
```

<a name="assert-button-enabled"></a>
#### assertButtonEnabled

断言给定按钮已启用：

```php
$browser->assertButtonEnabled($button);
```

<a name="assert-button-disabled"></a>
#### assertButtonDisabled

断言给定按钮已禁用：

```php
$browser->assertButtonDisabled($button);
```

<a name="assert-focused"></a>
#### assertFocused

断言给定字段已获得焦点：

```php
$browser->assertFocused($field);
```

<a name="assert-not-focused"></a>
#### assertNotFocused

断言给定字段未获得焦点：

```php
$browser->assertNotFocused($field);
```

<a name="assert-authenticated"></a>
#### assertAuthenticated

断言用户已通过身份验证：

```php
$browser->assertAuthenticated();
```

<a name="assert-guest"></a>
#### assertGuest

断言用户未通过身份验证：

```php
$browser->assertGuest();
```

<a name="assert-authenticated-as"></a>
#### assertAuthenticatedAs

断言当前已认证用户为给定用户：

```php
$browser->assertAuthenticatedAs($user);
```

<a name="assert-vue"></a>
#### assertVue

Dusk 甚至允许你对 [Vue 组件](https://vuejs.org)的数据状态进行断言。例如，假设应用中包含以下 Vue 组件：

    // HTML 示例……

    <profile dusk="profile-component"></profile>

    // 组件定义……

    Vue.component('profile', {
        template: '<div>{{ user.name }}</div>',

        data: function () {
            return {
                user: {
                    name: 'Taylor'
                }
            };
        }
    });

你可以像下面这样，对 Vue 组件的状态进行断言：

```php tab=Pest
test('vue', function () {
    $this->browse(function (Browser $browser) {
        $browser->visit('/')
            ->assertVue('user.name', 'Taylor', '@profile-component');
    });
});
```

```php tab=PHPUnit
/**
 * 一个基本的 Vue 测试示例。
 */
public function test_vue(): void
{
    $this->browse(function (Browser $browser) {
        $browser->visit('/')
            ->assertVue('user.name', 'Taylor', '@profile-component');
    });
}
```

<a name="assert-vue-is-not"></a>
#### assertVueIsNot

断言给定 Vue 组件的数据属性与给定值不匹配：

```php
$browser->assertVueIsNot($property, $value, $componentSelector = null);
```

<a name="assert-vue-contains"></a>
#### assertVueContains

断言给定 Vue 组件的数据属性为数组，且包含给定值：

```php
$browser->assertVueContains($property, $value, $componentSelector = null);
```

<a name="assert-vue-doesnt-contain"></a>
#### assertVueDoesntContain

断言给定 Vue 组件的数据属性为数组，且不包含给定值：

```php
$browser->assertVueDoesntContain($property, $value, $componentSelector = null);
```

<a name="pages"></a>
## 页面

有时，测试需要按顺序执行多项复杂操作，这会让测试难以阅读和理解。Dusk 页面允许你定义清晰易读的操作，随后通过单个方法在指定页面上执行。页面还允许你为整个应用或单个页面的常用选择器定义简写。

<a name="generating-pages"></a>
### 生成页面

要生成页面对象，请执行 `dusk:page` Artisan 命令。所有页面对象都会放在应用的 `tests/Browser/Pages` 目录中：

```shell
php artisan dusk:page Login
```

<a name="configuring-pages"></a>
### 配置页面

默认情况下，页面有三个方法：`url`、`assert` 和 `elements`。下面先介绍 `url` 和 `assert` 方法，`elements` 方法会在[后文详细介绍](#shorthand-selectors)。

<a name="the-url-method"></a>
#### `url` 方法

`url` 方法应该返回该页面对应的 URL 路径。Dusk 在浏览器中导航到该页面时，会使用这个 URL：

```php
/**
 * 获取页面的 URL。
 */
public function url(): string
{
    return '/login';
}
```

<a name="the-assert-method"></a>
#### `assert` 方法

`assert` 方法可以执行必要的断言，验证浏览器确实位于给定页面上。该方法可以留空，也可以根据需要加入断言。这些断言会在导航到该页面时自动执行：

```php
/**
 * 断言浏览器位于该页面。
 */
public function assert(Browser $browser): void
{
    $browser->assertPathIs($this->url());
}
```

<a name="navigating-to-pages"></a>
### 导航到页面

定义页面后，你可以使用 `visit` 方法导航到该页面：

```php
use Tests\Browser\Pages\Login;

$browser->visit(new Login);
```

有时，你可能已经位于给定页面上，需要将页面的选择器和方法「加载」到当前测试上下文中。例如，点击按钮后重定向到了某个页面，而没有显式导航到该页面时，就常会遇到这种情况。此时，你可以使用 `on` 方法加载页面：

```php
use Tests\Browser\Pages\CreatePlaylist;

$browser->visit('/dashboard')
    ->clickLink('Create Playlist')
    ->on(new CreatePlaylist)
    ->assertSee('@create');
```

<a name="shorthand-selectors"></a>
### 简写选择器

页面类的 `elements` 方法允许你为页面上的任意 CSS 选择器定义简短、易记的简写。例如，为应用登录页面的「email」输入字段定义简写：

```php
/**
 * 获取页面的元素简写。
 *
 * @return array<string, string>
 */
public function elements(): array
{
    return [
        '@email' => 'input[name=email]',
    ];
}
```

定义简写后，你可以在任何通常使用完整 CSS 选择器的地方使用该简写选择器：

```php
$browser->type('@email', 'taylor@laravel.com');
```

<a name="global-shorthand-selectors"></a>
#### 全局简写选择器

安装 Dusk 后，`tests/Browser/Pages` 目录中会生成一个 `Page` 基类。该类包含 `siteElements` 方法，可用于定义在整个应用的每个页面中都可用的全局简写选择器：

```php
/**
 * 获取站点的全局元素简写。
 *
 * @return array<string, string>
 */
public static function siteElements(): array
{
    return [
        '@element' => '#selector',
    ];
}
```

<a name="page-methods"></a>
### 页面方法

除了页面上默认定义的方法，你还可以定义其他方法，供测试复用。例如，假设我们正在构建一个音乐管理应用，某个页面上的常见操作是创建播放列表。你可以在页面类中定义 `createPlaylist` 方法，避免在每个测试中重复编写创建播放列表的逻辑：

```php
<?php

namespace Tests\Browser\Pages;

use Laravel\Dusk\Browser;
use Laravel\Dusk\Page;

class Dashboard extends Page
{
    // 其他页面方法……

    /**
     * 创建新的播放列表。
     */
    public function createPlaylist(Browser $browser, string $name): void
    {
        $browser->type('name', $name)
            ->check('share')
            ->press('Create Playlist');
    }
}
```

定义方法后，你可以在任何使用该页面的测试中调用它。浏览器实例会自动作为第一个参数传入自定义页面方法：

```php
use Tests\Browser\Pages\Dashboard;

$browser->visit(new Dashboard)
    ->createPlaylist('My Playlist')
    ->assertSee('My Playlist');
```

<a name="components"></a>
## 组件

组件类似于 Dusk 的「页面对象」，但用于在整个应用中复用的界面和功能片段，例如导航栏或通知窗口。因此，组件不绑定特定的 URL。

<a name="generating-components"></a>
### 生成组件

要生成组件，请执行 `dusk:component` Artisan 命令。新组件会放在 `tests/Browser/Components` 目录中：

```shell
php artisan dusk:component DatePicker
```

如上所示，「日期选择器」就是一种可能出现在应用多个页面中的组件。如果在整个测试套件的数十个测试中，都手动编写选择日期的浏览器自动化逻辑，会很繁琐。我们可以定义一个代表日期选择器的 Dusk 组件，将这些逻辑封装在组件中：

```php
<?php

namespace Tests\Browser\Components;

use Laravel\Dusk\Browser;
use Laravel\Dusk\Component as BaseComponent;

class DatePicker extends BaseComponent
{
    /**
     * 获取组件的根选择器。
     */
    public function selector(): string
    {
        return '.date-picker';
    }

    /**
     * 断言浏览器页面包含该组件。
     */
    public function assert(Browser $browser): void
    {
        $browser->assertVisible($this->selector());
    }

    /**
     * 获取组件的元素简写。
     *
     * @return array<string, string>
     */
    public function elements(): array
    {
        return [
            '@date-field' => 'input.datepicker-input',
            '@year-list' => 'div > div.datepicker-years',
            '@month-list' => 'div > div.datepicker-months',
            '@day-list' => 'div > div.datepicker-days',
        ];
    }

    /**
     * 选择给定的日期。
     */
    public function selectDate(Browser $browser, int $year, int $month, int $day): void
    {
        $browser->click('@date-field')
            ->within('@year-list', function (Browser $browser) use ($year) {
                $browser->click($year);
            })
            ->within('@month-list', function (Browser $browser) use ($month) {
                $browser->click($month);
            })
            ->within('@day-list', function (Browser $browser) use ($day) {
                $browser->click($day);
            });
    }
}
```

<a name="using-components"></a>
### 使用组件

定义组件后，我们就可以在任意测试中，轻松地通过日期选择器选择日期。如果选择日期的逻辑发生变化，只需更新组件即可：

```php tab=Pest
<?php

use Illuminate\Foundation\Testing\DatabaseMigrations;
use Tests\Browser\Components\DatePicker;

pest()->use(DatabaseMigrations::class);

test('basic example', function () {
    $this->browse(function (Browser $browser) {
        $browser->visit('/')
            ->within(new DatePicker, function (Browser $browser) {
                $browser->selectDate(2019, 1, 30);
            })
            ->assertSee('January');
    });
});
```

```php tab=PHPUnit
<?php

namespace Tests\Browser;

use Illuminate\Foundation\Testing\DatabaseMigrations;
use Laravel\Dusk\Browser;
use Tests\Browser\Components\DatePicker;
use Tests\DuskTestCase;

class ExampleTest extends DuskTestCase
{
    /**
     * 一个基本的组件测试示例。
     */
    public function test_basic_example(): void
    {
        $this->browse(function (Browser $browser) {
            $browser->visit('/')
                ->within(new DatePicker, function (Browser $browser) {
                    $browser->selectDate(2019, 1, 30);
                })
                ->assertSee('January');
        });
    }
}
```

你可以使用 `component` 方法，获取作用域限定在给定组件中的浏览器实例：

```php
$datePicker = $browser->component(new DatePickerComponent);

$datePicker->selectDate(2019, 1, 30);

$datePicker->assertSee('January');
```

<a name="continuous-integration"></a>
## 持续集成

> [!WARNING]
> 大多数 Dusk 持续集成配置都要求 Laravel 应用通过 PHP 内置开发服务器在 8000 端口提供服务。因此，继续之前，请确保持续集成环境的 `APP_URL` 环境变量值为 `http://127.0.0.1:8000`。

<a name="running-tests-on-heroku-ci"></a>
### Heroku CI

要在 [Heroku CI](https://www.heroku.com/continuous-integration) 上运行 Dusk 测试，请在 Heroku 的 `app.json` 文件中添加以下 Google Chrome buildpack 和脚本：

```json
{
  "environments": {
    "test": {
      "buildpacks": [
        { "url": "heroku/php" },
        { "url": "https://github.com/heroku/heroku-buildpack-chrome-for-testing" }
      ],
      "scripts": {
        "test-setup": "cp .env.testing .env",
        "test": "nohup bash -c './vendor/laravel/dusk/bin/chromedriver-linux --port=9515 > /dev/null 2>&1 &' && nohup bash -c 'php artisan serve --no-reload > /dev/null 2>&1 &' && php artisan dusk"
      }
    }
  }
}
```

<a name="running-tests-on-travis-ci"></a>
### Travis CI

要在 [Travis CI](https://travis-ci.org) 上运行 Dusk 测试，请使用以下 `.travis.yml` 配置。Travis CI 没有图形界面，因此需要额外的步骤来启动 Chrome 浏览器。此外，我们将使用 `php artisan serve` 启动 PHP 内置 Web 服务器：

```yaml
language: php

php:
  - 8.2

addons:
  chrome: stable

install:
  - cp .env.testing .env
  - travis_retry composer install --no-interaction --prefer-dist
  - php artisan key:generate
  - php artisan dusk:chrome-driver

before_script:
  - google-chrome-stable --headless --disable-gpu --remote-debugging-port=9222 http://localhost &
  - php artisan serve --no-reload &

script:
  - php artisan dusk
```

<a name="running-tests-on-github-actions"></a>
### GitHub Actions

如果你使用 [GitHub Actions](https://github.com/features/actions) 运行 Dusk 测试，可以将以下配置文件作为起点。与 Travis CI 一样，我们将使用 `php artisan serve` 命令启动 PHP 内置 Web 服务器：

```yaml
name: CI
on: [push]
jobs:

  dusk-php:
    runs-on: ubuntu-latest
    env:
      APP_URL: "http://127.0.0.1:8000"
      DB_USERNAME: root
      DB_PASSWORD: root
      MAIL_MAILER: log
    steps:
      - uses: actions/checkout@v5
      - name: Prepare The Environment
        run: cp .env.example .env
      - name: Create Database
        run: |
          sudo systemctl start mysql
          mysql --user="root" --password="root" -e "CREATE DATABASE \`my-database\` character set UTF8mb4 collate utf8mb4_bin;"
      - name: Install Composer Dependencies
        run: composer install --no-progress --prefer-dist --optimize-autoloader
      - name: Generate Application Key
        run: php artisan key:generate
      - name: Upgrade Chrome Driver
        run: php artisan dusk:chrome-driver --detect
      - name: Start Chrome Driver
        run: ./vendor/laravel/dusk/bin/chromedriver-linux --port=9515 &
      - name: Run Laravel Server
        run: php artisan serve --no-reload &
      - name: Run Dusk Tests
        run: php artisan dusk
      - name: Upload Screenshots
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: screenshots
          path: tests/Browser/screenshots
      - name: Upload Console Logs
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: console
          path: tests/Browser/console
```

<a name="running-tests-on-chipper-ci"></a>
### Chipper CI

如果你使用 [Chipper CI](https://chipperci.com) 运行 Dusk 测试，可以将以下配置文件作为起点。我们将使用 PHP 内置服务器运行 Laravel，以便监听请求：

```yaml
# 文件 .chipperci.yml
version: 1

environment:
  php: 8.2
  node: 16

# 在构建环境中包含 Chrome
services:
  - dusk

# 构建所有提交
on:
   push:
      branches: .*

pipeline:
  - name: Setup
    cmd: |
      cp -v .env.example .env
      composer install --no-interaction --prefer-dist --optimize-autoloader
      php artisan key:generate

      # 创建 Dusk 环境文件，确保 APP_URL 使用 BUILD_HOST
      cp -v .env .env.dusk.ci
      sed -i "s@APP_URL=.*@APP_URL=http://$BUILD_HOST:8000@g" .env.dusk.ci

  - name: Compile Assets
    cmd: |
      npm ci --no-audit
      npm run build

  - name: Browser Tests
    cmd: |
      php -S [::0]:8000 -t public 2>server.log &
      sleep 2
      php artisan dusk:chrome-driver $CHROME_DRIVER
      php artisan dusk --env=ci
```

要进一步了解如何在 Chipper CI 上运行 Dusk 测试（包括如何使用数据库），请参阅 [Chipper CI 官方文档](https://chipperci.com/docs/testing/laravel-dusk-new/)。
