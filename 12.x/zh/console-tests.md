
# 控制台测试（Console Tests）

-   [简介](#introduction)
-   [成功 / 失败预期](#success-failure-expectations)
-   [输入 / 输出预期](#input-output-expectations)
-   [控制台事件](#console-events)

## 简介

除了简化 HTTP 测试之外，Laravel 还为测试你的应用中的[自定义 Artisan 命令](/docs/laravel/12.x/artisan)提供了一个简洁的 API。

## 成功 / 失败预期

首先，让我们看看如何对 Artisan 命令的退出码进行断言。你可以使用 `artisan` 方法在测试中调用 Artisan 命令，然后使用 `assertExitCode` 方法断言该命令是否以特定退出码完成：

```php tab=Pest
test('console command', function () {
    $this->artisan('inspire')->assertExitCode(0);
});
```

```php tab=PHPUnit
/**
 * 测试一个控制台命令。
 */
public function test_console_command(): void
{
    $this->artisan('inspire')->assertExitCode(0);
}
```

你也可以使用 `assertNotExitCode` 方法，断言命令没有以某个特定退出码结束：

```php
$this->artisan('inspire')->assertNotExitCode(1);
```

通常情况下，终端命令在成功时会返回退出码 `0`，失败时则返回非零退出码。因此，你可以使用更直观的辅助方法 `assertSuccessful` 和 `assertFailed` 来分别断言命令是否成功执行或执行失败：

```php
$this->artisan('inspire')->assertSuccessful();

$this->artisan('inspire')->assertFailed();
```

## 输入 / 输出预期

Laravel 允许你使用 `expectsQuestion` 方法轻松「模拟」控制台命令中的用户输入。此外，你还可以使用 `assertExitCode` 和 `expectsOutput` 方法指定你期望命令的退出码以及输出的文本。例如，考虑下面这个控制台命令：

```php
Artisan::command('question', function () {
    $name = $this->ask('What is your name?');

    $language = $this->choice('Which language do you prefer?', [
        'PHP',
        'Ruby',
        'Python',
    ]);

    $this->line('Your name is '.$name.' and you prefer '.$language.'.');
});
```



你可以使用如下测试代码来测试该命令：

```php tab=Pest
test('console command', function () {
    $this->artisan('question')
        ->expectsQuestion('What is your name?', 'Taylor Otwell')
        ->expectsQuestion('Which language do you prefer?', 'PHP')
        ->expectsOutput('Your name is Taylor Otwell and you prefer PHP.')
        ->doesntExpectOutput('Your name is Taylor Otwell and you prefer Ruby.')
        ->assertExitCode(0);
});
```

```php tab=PHPUnit
/**
 * 测试一个控制台命令。
 */
public function test_console_command(): void
{
    $this->artisan('question')
        ->expectsQuestion('What is your name?', 'Taylor Otwell')
        ->expectsQuestion('Which language do you prefer?', 'PHP')
        ->expectsOutput('Your name is Taylor Otwell and you prefer PHP.')
        ->doesntExpectOutput('Your name is Taylor Otwell and you prefer Ruby.')
        ->assertExitCode(0);
}
```

如果你使用了 [Laravel Prompts](/docs/laravel/12.x/prompts) 提供的 `search` 或 `multisearch` 功能，可以使用 `expectsSearch` 方法来模拟用户的搜索行为、搜索结果及最终选择内容：

```php tab=Pest
test('console command', function () {
    $this->artisan('example')
        ->expectsSearch('What is your name?', search: 'Tay', answers: [
            'Taylor Otwell',
            'Taylor Swift',
            'Darian Taylor'
        ], answer: 'Taylor Otwell')
        ->assertExitCode(0);
});
```

```php tab=PHPUnit
/**
 * 测试一个控制台命令。
 */
public function test_console_command(): void
{
    $this->artisan('example')
        ->expectsSearch('What is your name?', search: 'Tay', answers: [
            'Taylor Otwell',
            'Taylor Swift',
            'Darian Taylor'
        ], answer: 'Taylor Otwell')
        ->assertExitCode(0);
}
```

你还可以使用 `doesntExpectOutput` 方法断言该命令在执行过程中**不会产生任何输出**：

```php tab=Pest
test('console command', function () {
    $this->artisan('example')
        ->doesntExpectOutput()
        ->assertExitCode(0);
});
```

```php tab=PHPUnit
/**
 * 测试一个控制台命令。
 */
public function test_console_command(): void
{
    $this->artisan('example')
        ->doesntExpectOutput()
        ->assertExitCode(0);
}
```



可以使用 `expectsOutputToContain` 和 `doesntExpectOutputToContain` 方法来断言命令输出中是否包含某个子字符串：

```php tab=Pest
test('console command', function () {
    $this->artisan('example')
        ->expectsOutputToContain('Taylor')
        ->assertExitCode(0);
});
```

```php tab=PHPUnit
/**
 * 测试一个控制台命令。
 */
public function test_console_command(): void
{
    $this->artisan('example')
        ->expectsOutputToContain('Taylor')
        ->assertExitCode(0);
}
```

#### 确认提示断言（Confirmation Expectations）

如果你的命令包含类似“是否继续？”这类是/否确认提示，你可以使用 `expectsConfirmation` 方法来模拟并断言用户的选择：

```php
$this->artisan('module:import')
    ->expectsConfirmation('Do you really wish to run this command?', 'no')
    ->assertExitCode(1);
```

#### 表格输出断言（Table Expectations）

如果你的命令使用 Artisan 的 `table` 方法展示表格，直接对完整输出做断言可能会很繁琐。此时可以使用 `expectsTable` 方法更简洁地验证表格输出内容：

```php
$this->artisan('users:all')
    ->expectsTable([
        'ID',
        'Email',
    ], [
        [1, 'taylor@example.com'],
        [2, 'abigail@example.com'],
    ]);
```

## 控制台事件（Console Events）

默认情况下，Laravel 在测试时**不会触发** `CommandStarting` 和 `CommandFinished` 两个控制台事件。如果你需要测试这些事件，可以在测试类中引入 `WithConsoleEvents` trait：

```php tab=Pest
<?php

use Illuminate\Foundation\Testing\WithConsoleEvents;

uses(WithConsoleEvents::class);

// ...
```

```php tab=PHPUnit
<?php

namespace Tests\Feature;

use Illuminate\Foundation\Testing\WithConsoleEvents;
use Tests\TestCase;

class ConsoleEventTest extends TestCase
{
    use WithConsoleEvents;

    // ...
}
```
