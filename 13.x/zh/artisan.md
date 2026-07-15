# Artisan 控制台

- [简介](#introduction)
    - [Tinker（REPL）](#tinker)
- [编写命令](#writing-commands)
    - [生成命令](#generating-commands)
    - [命令结构](#command-structure)
    - [闭包命令](#closure-commands)
    - [可隔离命令](#isolatable-commands)
- [定义输入预期](#defining-input-expectations)
    - [参数](#arguments)
    - [选项](#options)
    - [输入数组](#input-arrays)
    - [输入说明](#input-descriptions)
    - [提示缺失的输入](#prompting-for-missing-input)
- [命令输入 / 输出](#command-io)
    - [获取输入](#retrieving-input)
    - [提示输入](#prompting-for-input)
    - [输出信息](#writing-output)
- [注册命令](#registering-commands)
- [以编程方式执行命令](#programmatically-executing-commands)
    - [从其他命令调用命令](#calling-commands-from-other-commands)
- [信号处理](#signal-handling)
- [自定义 Stub](#stub-customization)
- [事件](#events)

<a name="introduction"></a>
## 简介

Artisan 是 Laravel 自带的命令行接口。Artisan 以 `artisan` 脚本的形式存在于应用根目录中，并提供了许多有用的命令，帮助你构建应用。可以使用 `list` 命令查看所有可用的 Artisan 命令：

```shell
php artisan list
```

每个命令还包含一个「帮助」界面，用于显示和说明该命令可用的参数与选项。若要查看帮助界面，请在命令名称前加上 `help`：

```shell
php artisan help migrate
```

<a name="laravel-sail"></a>
#### Laravel Sail

如果使用 [Laravel Sail](/docs/{{version}}/sail) 作为本地开发环境，请记得使用 `sail` 命令行调用 Artisan 命令。Sail 会在应用的 Docker 容器中执行 Artisan 命令：

```shell
./vendor/bin/sail artisan list
```

<a name="tinker"></a>
### Tinker（REPL）

[Laravel Tinker](https://github.com/laravel/tinker) 是一个功能强大的 Laravel 框架 REPL，由 [PsySH](https://github.com/bobthecow/psysh) 软件包驱动。

<a name="installation"></a>
#### 安装

所有 Laravel 应用默认都包含 Tinker。不过，如果之前已从应用中移除 Tinker，可以使用 Composer 重新安装：

```shell
composer require laravel/tinker
```

> [!NOTE]
> 想在与 Laravel 应用交互时获得热重载、多行代码编辑和自动补全功能？不妨试试 [Tinkerwell](https://tinkerwell.app)！

<a name="usage"></a>
#### 使用方法

Tinker 允许你通过命令行与整个 Laravel 应用交互，包括 Eloquent 模型、任务、事件等。若要进入 Tinker 环境，请运行 `tinker` Artisan 命令：

```shell
php artisan tinker
```

可以使用 `vendor:publish` 命令发布 Tinker 的配置文件：

```shell
php artisan vendor:publish --provider="Laravel\Tinker\TinkerServiceProvider"
```

> [!WARNING]
> `dispatch` 辅助函数和 `Dispatchable` 类的 `dispatch` 方法依赖垃圾回收机制将任务放入队列。因此，使用 Tinker 时，应使用 `Bus::dispatch` 或 `Queue::push` 来分发任务。

<a name="command-allow-list"></a>
#### 命令允许列表

Tinker 使用「允许」列表来确定可以在其交互环境中运行哪些 Artisan 命令。默认情况下，可以运行 `clear-compiled`、`down`、`env`、`inspire`、`migrate`、`migrate:install`、`up` 和 `optimize` 命令。如果要允许更多命令，可以将它们添加到 `tinker.php` 配置文件的 `commands` 数组中：

```php
'commands' => [
    // App\Console\Commands\ExampleCommand::class,
],
```

<a name="classes-that-should-not-be-aliased"></a>
#### 不应设置别名的类

通常，在 Tinker 中与类交互时，Tinker 会自动为类设置别名。不过，你可能不希望为某些类设置别名。为此，可以在 `tinker.php` 配置文件的 `dont_alias` 数组中列出这些类：

```php
'dont_alias' => [
    App\Models\User::class,
],
```

<a name="writing-commands"></a>
## 编写命令

除了 Artisan 自带的命令外，你还可以构建自己的自定义命令。命令通常存储在 `app/Console/Commands` 目录中；不过，只要指示 Laravel [扫描其他目录中的 Artisan 命令](#registering-commands)，也可以自由选择其他存储位置。

<a name="generating-commands"></a>
### 生成命令

若要创建新命令，可以使用 `make:command` Artisan 命令。该命令会在 `app/Console/Commands` 目录中创建一个新的命令类。如果应用中不存在此目录，不必担心——第一次运行 `make:command` Artisan 命令时，它会自动创建：

```shell
php artisan make:command SendEmails
```

<a name="command-structure"></a>
### 命令结构

生成命令后，应使用 `Signature` 和 `Description` 属性定义命令的签名和描述。`Signature` 属性还允许你定义[命令的输入预期](#defining-input-expectations)。执行命令时会调用 `handle` 方法，你可以将命令逻辑放在此方法中。

下面来看一个示例命令。请注意，可以通过命令的 `handle` 方法请求所需的任何依赖。Laravel [服务容器](/docs/{{version}}/container)会自动注入此方法签名中所有使用类型提示声明的依赖：

```php
<?php

namespace App\Console\Commands;

use App\Models\User;
use App\Support\DripEmailer;
use Illuminate\Console\Attributes\Description;
use Illuminate\Console\Attributes\Signature;
use Illuminate\Console\Command;

#[Signature('mail:send {user}')]
#[Description('Send a marketing email to a user')]
class SendEmails extends Command
{
    /**
     * 执行控制台命令。
     */
    public function handle(DripEmailer $drip): void
    {
        $drip->send(User::find($this->argument('user')));
    }
}
```

> [!NOTE]
> 为了更好地复用代码，建议保持控制台命令简洁，并让它们将任务委托给应用服务完成。在上面的示例中，请注意我们注入了一个服务类来承担发送电子邮件的「繁重工作」。

<a name="exit-codes"></a>
#### 退出码

如果 `handle` 方法没有返回任何内容且命令执行成功，命令将以 `0` 退出码退出，表示执行成功。不过，`handle` 方法也可以选择返回一个整数，以手动指定命令的退出码：

```php
$this->error('Something went wrong.');

return 1;
```

如果要从命令中的任意方法将命令标记为「失败」，可以使用 `fail` 方法。`fail` 方法会立即终止命令执行，并返回退出码 `1`：

```php
$this->fail('Something went wrong.');
```

<a name="closure-commands"></a>
### 闭包命令

基于闭包的命令提供了另一种定义控制台命令的方式，无须将其定义为类。正如路由闭包可以替代控制器一样，可以将命令闭包视为命令类的替代方案。

虽然 `routes/console.php` 文件不定义 HTTP 路由，但它定义了进入应用的控制台入口点（路由）。在此文件中，可以使用 `Artisan::command` 方法定义所有基于闭包的控制台命令。`command` 方法接受两个参数：[命令签名](#defining-input-expectations)，以及一个接收命令参数和选项的闭包：

```php
Artisan::command('mail:send {user}', function (string $user) {
    $this->info("Sending email to: {$user}!");
});
```

该闭包会绑定到底层命令实例，因此可以完全访问完整命令类中通常可用的所有辅助方法。

<a name="type-hinting-dependencies"></a>
#### 使用类型提示声明依赖

除了接收命令的参数和选项外，命令闭包还可以使用类型提示声明需要从[服务容器](/docs/{{version}}/container)中解析的其他依赖：

```php
use App\Models\User;
use App\Support\DripEmailer;
use Illuminate\Support\Facades\Artisan;

Artisan::command('mail:send {user}', function (DripEmailer $drip, string $user) {
    $drip->send(User::find($user));
});
```

<a name="closure-command-descriptions"></a>
#### 闭包命令描述

定义基于闭包的命令时，可以使用 `purpose` 方法为命令添加描述。运行 `php artisan list` 或 `php artisan help` 命令时会显示此描述：

```php
Artisan::command('mail:send {user}', function (string $user) {
    // ...
})->purpose('Send a marketing email to a user');
```

<a name="isolatable-commands"></a>
### 可隔离命令

> [!WARNING]
> 若要使用此功能，应用必须将 `memcached`、`redis`、`dynamodb`、`database`、`file` 或 `array` 缓存驱动作为默认缓存驱动。此外，所有服务器必须与同一个中央缓存服务器通信。

有时，你可能希望确保同一时间只能运行一个命令实例。为此，可以让命令类实现 `Illuminate\Contracts\Console\Isolatable` 接口：

```php
<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;
use Illuminate\Contracts\Console\Isolatable;

class SendEmails extends Command implements Isolatable
{
    // ...
}
```

将命令标记为 `Isolatable` 后，Laravel 会自动为该命令提供 `--isolated` 选项，无须在命令选项中显式定义。使用该选项调用命令时，Laravel 会确保没有该命令的其他实例正在运行。Laravel 通过应用的默认缓存驱动尝试获取原子锁来实现这一点。如果该命令的其他实例正在运行，命令将不会执行；但是，它仍会以成功状态码退出：

```shell
php artisan mail:send 1 --isolated
```

如果要指定命令无法执行时应返回的退出状态码，可以通过 `isolated` 选项提供所需的状态码：

```shell
php artisan mail:send 1 --isolated=12
```

<a name="lock-id"></a>
#### 锁 ID

默认情况下，Laravel 使用命令名称生成用于在应用缓存中获取原子锁的字符串键。不过，可以在 Artisan 命令类中定义 `isolatableId` 方法来自定义此键，从而将命令参数或选项整合到键中：

```php
/**
 * 获取命令的可隔离 ID。
 */
public function isolatableId(): string
{
    return $this->argument('user');
}
```

<a name="lock-expiration-time"></a>
#### 锁过期时间

默认情况下，隔离锁会在命令执行完毕后过期。如果命令中断而无法完成，锁会在一小时后过期。不过，可以在命令中定义 `isolationLockExpiresAt` 方法来调整锁的过期时间：

```php
use DateTimeInterface;
use DateInterval;

/**
 * 确定命令的隔离锁何时过期。
 */
public function isolationLockExpiresAt(): DateTimeInterface|DateInterval
{
    return now()->plus(minutes: 5);
}
```

<a name="defining-input-expectations"></a>
## 定义输入预期

编写控制台命令时，通常需要通过参数或选项收集用户输入。Laravel 让你可以通过命令的 `signature` 属性非常方便地定义预期从用户处获取的输入。`signature` 属性允许你使用一种富有表现力、类似路由的语法，在一处定义命令的名称、参数和选项。

<a name="arguments"></a>
### 参数

用户提供的所有参数和选项都用花括号括起。在以下示例中，命令定义了一个必填参数：`user`：

```php
/**
 * 控制台命令的名称和签名。
 *
 * @var string
 */
protected $signature = 'mail:send {user}';
```

也可以将参数设为可选，或为参数定义默认值：

```php
// 可选参数...
'mail:send {user?}'

// 带默认值的可选参数...
'mail:send {user=foo}'
```

<a name="options"></a>
### 选项

选项与参数一样，也是用户输入的一种形式。通过命令行提供选项时，选项以两个连字符（`--`）开头。选项分为两类：接收值的选项和不接收值的选项。不接收值的选项用作布尔「开关」。下面来看一个这种选项的示例：

```php
/**
 * 控制台命令的名称和签名。
 *
 * @var string
 */
protected $signature = 'mail:send {user} {--queue}';
```

在此示例中，调用 Artisan 命令时可以指定 `--queue` 开关。如果传入 `--queue` 开关，该选项的值将为 `true`；否则，其值将为 `false`：

```shell
php artisan mail:send 1 --queue
```

<a name="options-with-values"></a>
#### 带值的选项

接下来，来看一个需要值的选项。如果用户必须为选项指定值，应在选项名称后加上 `=` 符号：

```php
/**
 * 控制台命令的名称和签名。
 *
 * @var string
 */
protected $signature = 'mail:send {user} {--queue=}';
```

在此示例中，用户可以按如下方式传递选项值。如果调用命令时未指定该选项，其值将为 `null`：

```shell
php artisan mail:send 1 --queue=default
```

可以在选项名称后指定默认值，为选项分配默认值。如果用户未传入选项值，将使用默认值：

```php
'mail:send {user} {--queue=default}'
```

<a name="option-shortcuts"></a>
#### 选项快捷方式

若要在定义选项时为其分配快捷方式，可以在选项名称前指定快捷方式，并使用 `|` 字符作为分隔符，将快捷方式与完整选项名称分隔开：

```php
'mail:send {user} {--Q|queue=}'
```

在终端调用命令时，选项快捷方式应以单个连字符开头；为选项指定值时，不应包含 `=` 字符：

```shell
php artisan mail:send 1 -Qdefault
```

<a name="input-arrays"></a>
### 输入数组

如果要定义接收多个输入值的参数或选项，可以使用 `*` 字符。首先，来看一个指定此类参数的示例：

```php
'mail:send {user*}'
```

运行此命令时，可以按顺序将多个 `user` 参数传入命令行。例如，以下命令会将 `user` 的值设置为包含 `1` 和 `2` 的数组：

```shell
php artisan mail:send 1 2
```

可以将 `*` 字符与可选参数定义结合使用，从而允许传入零个或多个参数：

```php
'mail:send {user?*}'
```

<a name="option-arrays"></a>
#### 选项数组

定义接收多个输入值的选项时，传给命令的每个选项值都应以选项名称作为前缀：

```php
'mail:send {--id=*}'
```

可以通过传入多个 `--id` 参数来调用此命令：

```shell
php artisan mail:send --id=1 --id=2
```

<a name="input-descriptions"></a>
### 输入说明

可以使用冒号分隔参数名称与说明，为输入参数和选项分配说明。如果需要更多空间来定义命令，可以将定义拆分到多行：

```php
/**
 * 控制台命令的名称和签名。
 *
 * @var string
 */
protected $signature = 'mail:send
                        {user : The ID of the user}
                        {--queue : Whether the job should be queued}';
```

<a name="prompting-for-missing-input"></a>
### 提示缺失的输入

如果命令包含必填参数，而用户没有提供这些参数，他们将收到错误消息。或者，也可以通过实现 `PromptsForMissingInput` 接口，将命令配置为在缺少必填参数时自动提示用户：

```php
<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;
use Illuminate\Contracts\Console\PromptsForMissingInput;

class SendEmails extends Command implements PromptsForMissingInput
{
    /**
     * 控制台命令的名称和签名。
     *
     * @var string
     */
    protected $signature = 'mail:send {user}';

    // ...
}
```

如果 Laravel 需要从用户处获取必填参数，它会使用参数名称或说明智能地组织问题措辞，并自动询问用户。如果要自定义用于获取必填参数的问题，可以实现 `promptForMissingArgumentsUsing` 方法，返回一个以参数名称为键的问题数组：

```php
/**
 * 使用返回的问题提示缺失的输入参数。
 *
 * @return array<string, string>
 */
protected function promptForMissingArgumentsUsing(): array
{
    return [
        'user' => 'Which user ID should receive the mail?',
    ];
}
```

还可以使用包含问题和占位文本的元组来提供占位文本：

```php
return [
    'user' => ['Which user ID should receive the mail?', 'E.g. 123'],
];
```

如果需要完全控制提示过程，可以提供一个闭包，由该闭包提示用户并返回其答案：

```php
use App\Models\User;
use function Laravel\Prompts\search;

// ...

return [
    'user' => fn () => search(
        label: 'Search for a user:',
        placeholder: 'E.g. Taylor Otwell',
        options: fn ($value) => strlen($value) > 0
            ? User::whereLike('name', "%{$value}%")->pluck('name', 'id')->all()
            : []
    ),
];
```

> [!NOTE]
> 完整的 [Laravel Prompts](/docs/{{version}}/prompts) 文档包含有关可用提示及其用法的更多信息。

如果要提示用户选择或输入[选项](#options)，可以在命令的 `handle` 方法中包含提示。不过，如果只想在用户已因缺失参数而收到自动提示时再提示用户，可以实现 `afterPromptingForMissingArguments` 方法：

```php
use Symfony\Component\Console\Input\InputInterface;
use Symfony\Component\Console\Output\OutputInterface;
use function Laravel\Prompts\confirm;

// ...

/**
 * 在提示用户输入缺失参数后执行操作。
 */
protected function afterPromptingForMissingArguments(InputInterface $input, OutputInterface $output): void
{
    $input->setOption('queue', confirm(
        label: 'Would you like to queue the mail?',
        default: $this->option('queue')
    ));
}
```

<a name="command-io"></a>
## 命令输入 / 输出

<a name="retrieving-input"></a>
### 获取输入

命令执行时，你很可能需要访问命令所接收的参数和选项值。为此，可以使用 `argument` 和 `option` 方法。如果参数或选项不存在，将返回 `null`：

```php
/**
 * 执行控制台命令。
 */
public function handle(): void
{
    $userId = $this->argument('user');
}
```

如果需要以 `array` 形式获取所有参数，请调用 `arguments` 方法：

```php
$arguments = $this->arguments();
```

使用 `option` 方法可以像获取参数一样轻松地获取选项。若要以数组形式获取所有选项，请调用 `options` 方法：

```php
// 获取特定选项...
$queueName = $this->option('queue');

// 以数组形式获取所有选项...
$options = $this->options();
```

可以使用 `input` 方法将命令的参数和选项获取为 `Illuminate\Console\CommandInput` 实例。该实例提供与 HTTP 请求和其他数据容器相同的类型化访问器：

```php
use App\Enums\ReportType;

/**
 * 执行控制台命令。
 */
public function handle(): void
{
    $input = $this->input()->date('from');

    // ...
}
```

也可以使用 `input` 方法从参数或选项中获取单个输入值：

```php
$queue = $this->input('queue', 'default');
```

<a name="prompting-for-input"></a>
### 提示输入

> [!NOTE]
> [Laravel Prompts](/docs/{{version}}/prompts) 是一个 PHP 软件包，用于为命令行应用添加美观且用户友好的表单，并提供占位文本和验证等类似浏览器的功能。

除了显示输出外，还可以在命令执行过程中请求用户提供输入。`ask` 方法会使用给定问题提示用户，接收用户输入，然后将其返回给命令：

```php
/**
 * 执行控制台命令。
 */
public function handle(): void
{
    $name = $this->ask('What is your name?');

    // ...
}
```

`ask` 方法还接受可选的第二个参数，用于指定未提供用户输入时应返回的默认值：

```php
$name = $this->ask('What is your name?', 'Taylor');
```

`secret` 方法与 `ask` 类似，但用户在控制台输入时看不到自己的输入。此方法适合用于请求密码等敏感信息：

```php
$password = $this->secret('What is the password?');
```

<a name="asking-for-confirmation"></a>
#### 请求确认

如果需要向用户请求简单的「是或否」确认，可以使用 `confirm` 方法。默认情况下，该方法返回 `false`。不过，如果用户在提示中输入 `y` 或 `yes`，该方法将返回 `true`。

```php
if ($this->confirm('Do you wish to continue?')) {
    // ...
}
```

如有必要，可以将 `true` 作为第二个参数传给 `confirm` 方法，使确认提示默认返回 `true`：

```php
if ($this->confirm('Do you wish to continue?', true)) {
    // ...
}
```

<a name="auto-completion"></a>
#### 自动补全

`anticipate` 方法可用于为可能的选项提供自动补全。无论自动补全提示为何，用户仍然可以提供任何答案：

```php
$name = $this->anticipate('What is your name?', ['Taylor', 'Dayle']);
```

也可以将闭包作为第二个参数传给 `anticipate` 方法。每当用户输入一个字符时，系统都会调用该闭包。闭包应接受一个字符串参数，其中包含用户当前已输入的内容，并返回一个用于自动补全的选项数组：

```php
use App\Models\Address;

$name = $this->anticipate('What is your address?', function (string $input) {
    return Address::whereLike('name', "{$input}%")
        ->limit(5)
        ->pluck('name')
        ->all();
});
```

<a name="multiple-choice-questions"></a>
#### 多项选择问题

如果提问时需要向用户提供一组预定义选项，可以使用 `choice` 方法。可以将默认值的数组索引作为第三个参数传给该方法，以设置用户未选择任何选项时返回的默认值：

```php
$name = $this->choice(
    'What is your name?',
    ['Taylor', 'Dayle'],
    $defaultIndex
);
```

此外，`choice` 方法接受可选的第四和第五个参数，分别用于确定选择有效答案的最大尝试次数，以及是否允许多选：

```php
$name = $this->choice(
    'What is your name?',
    ['Taylor', 'Dayle'],
    $defaultIndex,
    $maxAttempts = null,
    $allowMultipleSelections = false
);
```

<a name="writing-output"></a>
### 输出信息

若要向控制台发送输出，可以使用 `line`、`newLine`、`info`、`comment`、`question`、`warn`、`alert` 和 `error` 方法。每种方法都会根据其用途使用合适的 ANSI 颜色。例如，下面向用户显示一些常规信息。通常，`info` 方法会在控制台中显示绿色文本：

```php
/**
 * 执行控制台命令。
 */
public function handle(): void
{
    // ...

    $this->info('The command was successful!');
}
```

若要显示错误消息，请使用 `error` 方法。错误消息文本通常显示为红色：

```php
$this->error('Something went wrong!');
```

可以使用 `line` 方法显示不带颜色的纯文本：

```php
$this->line('Display this on the screen');
```

可以使用 `newLine` 方法显示空行：

```php
// 写入一个空行...
$this->newLine();

// 写入三个空行...
$this->newLine(3);
```

<a name="tables"></a>
#### 表格

`table` 方法让你可以轻松地正确格式化多行、多列数据。只需提供列名和表格数据，Laravel 就会自动计算表格的合适宽度和高度：

```php
use App\Models\User;

$this->table(
    ['Name', 'Email'],
    User::all(['name', 'email'])->toArray()
);
```

<a name="progress-bars"></a>
#### 进度条

对于长时间运行的任务，显示进度条有助于告知用户任务的完成程度。使用 `withProgressBar` 方法时，Laravel 会显示进度条，并在每次迭代给定的可迭代值时推进进度：

```php
use App\Models\User;

$users = $this->withProgressBar(User::all(), function (User $user) {
    $this->performTask($user);
});
```

有时，你可能需要更精细地手动控制进度条的推进方式。首先，定义进程将迭代的总步数。然后，在处理每个项目后推进进度条：

```php
$users = App\Models\User::all();

$bar = $this->output->createProgressBar(count($users));

$bar->start();

foreach ($users as $user) {
    $this->performTask($user);

    $bar->advance();
}

$bar->finish();
```

> [!NOTE]
> 如需了解更高级的选项，请参阅 [Symfony 进度条组件文档](https://symfony.com/doc/current/components/console/helpers/progressbar.html)。

<a name="registering-commands"></a>
## 注册命令

默认情况下，Laravel 会自动注册 `app/Console/Commands` 目录中的所有命令。不过，可以在应用的 `bootstrap/app.php` 文件中使用 `withCommands` 方法，指示 Laravel 扫描其他目录中的 Artisan 命令：

```php
->withCommands([
    __DIR__.'/../app/Domain/Orders/Commands',
])
```

如有必要，也可以将命令的类名提供给 `withCommands` 方法，以手动注册命令：

```php
use App\Domain\Orders\Commands\SendEmails;

->withCommands([
    SendEmails::class,
])
```

Artisan 启动时，应用中的所有命令都会由[服务容器](/docs/{{version}}/container)解析，并注册到 Artisan。

<a name="programmatically-executing-commands"></a>
## 以编程方式执行命令

有时，你可能希望在 CLI 之外执行 Artisan 命令。例如，可能需要从路由或控制器中执行 Artisan 命令。可以使用 `Artisan` 门面的 `call` 方法来实现。`call` 方法接受命令的签名名称或类名作为第一个参数，并接受命令参数数组作为第二个参数。该方法会返回退出码：

```php
use Illuminate\Support\Facades\Artisan;
use Illuminate\Support\Facades\Route;

Route::post('/user/{user}/mail', function (string $user) {
    $exitCode = Artisan::call('mail:send', [
        'user' => $user, '--queue' => 'default'
    ]);

    // ...
});
```

或者，也可以将完整的 Artisan 命令以字符串形式传给 `call` 方法：

```php
Artisan::call('mail:send 1 --queue=default');
```

<a name="passing-array-values"></a>
#### 传递数组值

如果命令定义了一个接收数组的选项，可以向该选项传递值数组：

```php
use Illuminate\Support\Facades\Artisan;
use Illuminate\Support\Facades\Route;

Route::post('/mail', function () {
    $exitCode = Artisan::call('mail:send', [
        '--id' => [5, 13]
    ]);
});
```

<a name="passing-boolean-values"></a>
#### 传递布尔值

如果需要为不接收字符串值的选项指定值，例如 `migrate:refresh` 命令的 `--force` 标志，应将 `true` 或 `false` 作为选项值传入：

```php
$exitCode = Artisan::call('migrate:refresh', [
    '--force' => true,
]);
```

<a name="queueing-artisan-commands"></a>
#### 将 Artisan 命令加入队列

使用 `Artisan` 门面的 `queue` 方法，甚至可以将 Artisan 命令加入队列，由[队列工作进程](/docs/{{version}}/queues)在后台处理。在使用此方法之前，请确保已配置队列并且正在运行队列监听器：

```php
use Illuminate\Support\Facades\Artisan;
use Illuminate\Support\Facades\Route;

Route::post('/user/{user}/mail', function (string $user) {
    Artisan::queue('mail:send', [
        'user' => $user, '--queue' => 'default'
    ]);

    // ...
});
```

可以使用 `onConnection` 和 `onQueue` 方法指定 Artisan 命令应分发到的连接或队列：

```php
Artisan::queue('mail:send', [
    'user' => 1, '--queue' => 'default'
])->onConnection('redis')->onQueue('commands');
```

<a name="calling-commands-from-other-commands"></a>
### 从其他命令调用命令

有时，你可能需要从现有 Artisan 命令中调用其他命令。可以使用 `call` 方法来实现。该方法接受命令名称和命令参数 / 选项数组：

```php
/**
 * 执行控制台命令。
 */
public function handle(): void
{
    $this->call('mail:send', [
        'user' => 1, '--queue' => 'default'
    ]);

    // ...
}
```

如果要调用另一个控制台命令并禁止其所有输出，可以使用 `callSilently` 方法。`callSilently` 方法的签名与 `call` 方法相同：

```php
$this->callSilently('mail:send', [
    'user' => 1, '--queue' => 'default'
]);
```

<a name="signal-handling"></a>
## 信号处理

你可能知道，操作系统允许向正在运行的进程发送信号。例如，操作系统使用 `SIGTERM` 信号请求程序正常终止。如果要在 Artisan 控制台命令中监听信号，并在收到信号时执行代码，可以使用 `trap` 方法：

```php
/**
 * 执行控制台命令。
 */
public function handle(): void
{
    $this->trap(SIGTERM, fn () => $this->shouldKeepRunning = false);

    while ($this->shouldKeepRunning) {
        // ...
    }
}
```

若要同时监听多个信号，可以向 `trap` 方法提供信号数组：

```php
$this->trap([SIGTERM, SIGQUIT], function (int $signal) {
    $this->shouldKeepRunning = false;

    dump($signal); // SIGTERM / SIGQUIT
});
```

<a name="stub-customization"></a>
## 自定义 Stub

Artisan 控制台的 `make` 命令用于创建控制器、任务、迁移和测试等各种类。这些类使用「Stub」文件生成，并根据你的输入填充值。不过，你可能希望对 Artisan 生成的文件做一些小修改。为此，可以使用 `stub:publish` 命令将最常用的 Stub 发布到应用中，以便进行自定义：

```shell
php artisan stub:publish
```

发布的 Stub 位于应用根目录的 `stubs` 目录中。对这些 Stub 所做的任何更改，都会在使用 Artisan 的 `make` 命令生成相应类时得到体现。

<a name="events"></a>
## 事件

运行命令时，Artisan 会分发三个事件：`Illuminate\Console\Events\ArtisanStarting`、`Illuminate\Console\Events\CommandStarting` 和 `Illuminate\Console\Events\CommandFinished`。Artisan 开始运行时会立即分发 `ArtisanStarting` 事件。接下来，命令运行前会立即分发 `CommandStarting` 事件。最后，命令执行完毕后会分发 `CommandFinished` 事件。
