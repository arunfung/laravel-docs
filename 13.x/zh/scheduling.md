# 任务调度

- [简介](#introduction)
- [定义调度](#defining-schedules)
    - [调度 Artisan 命令](#scheduling-artisan-commands)
    - [调度队列作业](#scheduling-queued-jobs)
    - [调度 Shell 命令](#scheduling-shell-commands)
    - [调度频率选项](#schedule-frequency-options)
    - [时区](#timezones)
    - [避免任务重叠](#preventing-task-overlaps)
    - [只在一台服务器上运行任务](#running-tasks-on-one-server)
    - [后台任务](#background-tasks)
    - [维护模式](#maintenance-mode)
    - [暂停调度任务](#pausing-scheduled-tasks)
    - [调度分组](#schedule-groups)
- [运行调度器](#running-the-scheduler)
    - [亚分钟级调度任务](#sub-minute-scheduled-tasks)
    - [在本地运行调度器](#running-the-scheduler-locally)
- [任务输出](#task-output)
- [任务钩子](#task-hooks)
- [事件](#events)

<a name="introduction"></a>
## 简介

过去，你可能需要为服务器上每个待调度的任务编写一条 cron 配置。但这种方式很快就会变得麻烦：任务调度配置不再受版本控制，你还必须通过 SSH 登录服务器，才能查看现有的 cron 条目或添加新条目。

Laravel 的命令调度器提供了一种管理服务器定时任务的新方式。你可以直接在 Laravel 应用程序中，以流畅、清晰的方式定义命令调度。使用调度器时，服务器只需要一条 cron 配置。任务调度通常定义在应用程序的 `routes/console.php` 文件中。

<a name="defining-schedules"></a>
## 定义调度

你可以在应用程序的 `routes/console.php` 文件中定义所有调度任务。先来看一个示例：我们将调度一个闭包，使其每天午夜执行，并在闭包中通过数据库查询清空一张表：

```php
<?php

use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schedule;

Schedule::call(function () {
    DB::table('recent_users')->delete();
})->daily();
```

除了闭包，你还可以调度 [可调用对象](https://secure.php.net/manual/en/language.oop5.magic.php#object.invoke)。可调用对象是包含 `__invoke` 方法的普通 PHP 类：

```php
Schedule::call(new DeleteRecentUsers)->daily();
```

如果你希望 `routes/console.php` 文件只用于定义命令，可以在应用程序的 `bootstrap/app.php` 文件中使用 `withSchedule` 方法定义调度任务。该方法接受一个闭包，并向闭包传入调度器实例：

```php
use Illuminate\Console\Scheduling\Schedule;

->withSchedule(function (Schedule $schedule) {
    $schedule->call(new DeleteRecentUsers)->daily();
})
```

如果你想查看调度任务的概览和下一次运行时间，可以使用 `schedule:list` Artisan 命令：

```shell
php artisan schedule:list
```

<a name="scheduling-artisan-commands"></a>
### 调度 Artisan 命令

除了闭包，你还可以调度 [Artisan 命令](/docs/{{version}}/artisan) 和系统命令。例如，你可以使用 `command` 方法，通过命令名称或命令类来调度 Artisan 命令。

使用命令类名调度 Artisan 命令时，你可以传入额外的命令行参数数组，在命令执行时提供这些参数：

```php
use App\Console\Commands\SendEmailsCommand;
use Illuminate\Support\Facades\Schedule;

Schedule::command('emails:send Taylor --force')->daily();

Schedule::command(SendEmailsCommand::class, ['Taylor', '--force'])->daily();
```

<a name="scheduling-artisan-closure-commands"></a>
#### 调度 Artisan 闭包命令

如果你想调度由闭包定义的 Artisan 命令，可以在命令定义后链式调用调度相关的方法：

```php
Artisan::command('delete:recent-users', function () {
    DB::table('recent_users')->delete();
})->purpose('Delete recent users')->daily();
```

如果需要向闭包命令传递参数，可以将它们传入 `schedule` 方法：

```php
Artisan::command('emails:send {user} {--force}', function ($user) {
    // ...
})->purpose('Send emails to the specified user')->schedule(['Taylor', '--force'])->daily();
```

<a name="scheduling-queued-jobs"></a>
### 调度队列作业

`job` 方法可用于调度 [队列作业](/docs/{{version}}/queues)。它提供了一种便捷的调度方式，无需使用 `call` 方法定义闭包来将作业加入队列：

```php
use App\Jobs\Heartbeat;
use Illuminate\Support\Facades\Schedule;

Schedule::job(new Heartbeat)->everyFiveMinutes();
```

你可以向 `job` 方法传入可选的第二个和第三个参数，分别指定将作业加入队列时使用的队列名称和队列连接：

```php
use App\Jobs\Heartbeat;
use Illuminate\Support\Facades\Schedule;

// 将作业分发到「sqs」连接上的「heartbeats」队列...
Schedule::job(new Heartbeat, 'heartbeats', 'sqs')->everyFiveMinutes();
```

<a name="scheduling-shell-commands"></a>
### 调度 Shell 命令

`exec` 方法可用于执行操作系统命令：

```php
use Illuminate\Support\Facades\Schedule;

Schedule::exec('node /home/forge/script.js')->daily();
```

<a name="schedule-frequency-options"></a>
### 调度频率选项

前面的示例展示了如何配置任务按指定的时间间隔运行。除此之外，你还可以为任务设置以下调度频率：

<div class="overflow-auto" markdown="1">

| 方法                             | 描述                                              |
| ---------------------------------- | -------------------------------------------------------- |
| `->cron('* * * * *');`             | 按自定义 cron 表达式运行任务。 |
| `->everySecond();`                 | 每秒运行一次任务。 |
| `->everyTwoSeconds();`             | 每 2 秒运行一次任务。 |
| `->everyFiveSeconds();`            | 每 5 秒运行一次任务。 |
| `->everyTenSeconds();`             | 每 10 秒运行一次任务。 |
| `->everyFifteenSeconds();`         | 每 15 秒运行一次任务。 |
| `->everyTwentySeconds();`          | 每 20 秒运行一次任务。 |
| `->everyThirtySeconds();`          | 每 30 秒运行一次任务。 |
| `->everyMinute();`                 | 每分钟运行一次任务。 |
| `->everyTwoMinutes();`             | 每 2 分钟运行一次任务。 |
| `->everyThreeMinutes();`           | 每 3 分钟运行一次任务。 |
| `->everyFourMinutes();`            | 每 4 分钟运行一次任务。 |
| `->everyFiveMinutes();`            | 每 5 分钟运行一次任务。 |
| `->everyTenMinutes();`             | 每 10 分钟运行一次任务。 |
| `->everyFifteenMinutes();`         | 每 15 分钟运行一次任务。 |
| `->everyThirtyMinutes();`          | 每 30 分钟运行一次任务。 |
| `->hourly();`                      | 每小时运行一次任务。 |
| `->hourlyAt(17);`                  | 每小时的第 17 分钟运行一次任务。 |
| `->everyOddHour($minutes = 0);`    | 每个奇数小时运行一次任务。 |
| `->everyTwoHours($minutes = 0);`   | 每 2 小时运行一次任务。 |
| `->everyThreeHours($minutes = 0);` | 每 3 小时运行一次任务。 |
| `->everyFourHours($minutes = 0);`  | 每 4 小时运行一次任务。 |
| `->everySixHours($minutes = 0);`   | 每 6 小时运行一次任务。 |
| `->daily();`                       | 每天午夜运行一次任务。 |
| `->dailyAt('13:00');`              | 每天 13:00 运行一次任务。 |
| `->twiceDaily(1, 13);`             | 每天 1:00 和 13:00 各运行一次任务。 |
| `->twiceDailyAt(1, 13, 15);`       | 每天 1:15 和 13:15 各运行一次任务。 |
| `->daysOfMonth([1, 10, 20]);`      | 每月的指定日期运行任务。 |
| `->weekly();`                      | 每周日 00:00 运行一次任务。 |
| `->weeklyOn(1, '8:00');`           | 每周一 8:00 运行一次任务。 |
| `->monthly();`                     | 每月第一天 00:00 运行一次任务。 |
| `->monthlyOn(4, '15:00');`         | 每月 4 日 15:00 运行一次任务。 |
| `->twiceMonthly(1, 16, '13:00');`  | 每月 1 日和 16 日 13:00 各运行一次任务。 |
| `->lastDayOfMonth('15:00');`       | 每月最后一天 15:00 运行一次任务。 |
| `->quarterly();`                   | 每季度第一天 00:00 运行一次任务。 |
| `->quarterlyOn(4, '14:00');`       | 每季度第 4 天 14:00 运行一次任务。 |
| `->yearly();`                      | 每年第一天 00:00 运行一次任务。 |
| `->yearlyOn(6, 1, '17:00');`       | 每年 6 月 1 日 17:00 运行一次任务。 |
| `->timezone('America/New_York');`  | 设置任务的时区。 |

</div>

这些方法可以与其他约束条件组合，进一步细化调度，使任务仅在一周中的特定日期运行。例如，你可以将命令安排为每周一运行：

```php
use Illuminate\Support\Facades\Schedule;

// 每周一下午 1 点运行一次...
Schedule::call(function () {
    // ...
})->weekly()->mondays()->at('13:00');

// 工作日上午 8 点至下午 5 点之间，每小时运行一次...
Schedule::command('foo')
    ->weekdays()
    ->hourly()
    ->timezone('America/Chicago')
    ->between('8:00', '17:00');
```

其他调度约束条件如下：

<div class="overflow-auto" markdown="1">

| 方法                                   | 描述                                            |
| ---------------------------------------- | ------------------------------------------------------ |
| `->weekdays();`                          | 仅在工作日运行任务。 |
| `->weekends();`                          | 仅在周末运行任务。 |
| `->sundays();`                           | 仅在周日运行任务。 |
| `->mondays();`                           | 仅在周一运行任务。 |
| `->tuesdays();`                          | 仅在周二运行任务。 |
| `->wednesdays();`                        | 仅在周三运行任务。 |
| `->thursdays();`                         | 仅在周四运行任务。 |
| `->fridays();`                           | 仅在周五运行任务。 |
| `->saturdays();`                         | 仅在周六运行任务。 |
| `->days(array\|mixed);`                  | 仅在一周中的指定日期运行任务。 |
| `->between($startTime, $endTime);`       | 仅在开始时间和结束时间之间运行任务。 |
| `->unlessBetween($startTime, $endTime);` | 不在开始时间和结束时间之间运行任务。 |
| `->when(Closure);`                       | 根据条件判断的结果决定是否运行任务。 |
| `->environments($env);`                  | 仅在指定环境中运行任务。 |

</div>

<a name="day-constraints"></a>
#### 星期约束

`days` 方法可用于限制任务仅在一周中的指定日期执行。例如，你可以调度命令，使其在周日和周三每小时运行一次：

```php
use Illuminate\Support\Facades\Schedule;

Schedule::command('emails:send')
    ->hourly()
    ->days([0, 3]);
```

你也可以使用 `Illuminate\Console\Scheduling\Schedule` 类提供的常量，定义任务应在哪些日期运行：

```php
use Illuminate\Support\Facades;
use Illuminate\Console\Scheduling\Schedule;

Facades\Schedule::command('emails:send')
    ->hourly()
    ->days([Schedule::SUNDAY, Schedule::WEDNESDAY]);
```

<a name="between-time-constraints"></a>
#### 时间区间约束

`between` 方法可用于限制任务在一天中的指定时间段执行：

```php
Schedule::command('emails:send')
    ->hourly()
    ->between('7:00', '22:00');
```

同样，`unlessBetween` 方法可用于排除任务在指定时间段内的执行：

```php
Schedule::command('emails:send')
    ->hourly()
    ->unlessBetween('23:00', '4:00');
```

<a name="truth-test-constraints"></a>
#### 条件判断约束

`when` 方法可根据给定条件判断的结果限制任务执行。换句话说，如果给定闭包返回 `true`，只要没有其他约束条件阻止任务运行，任务就会执行：

```php
Schedule::command('emails:send')->daily()->when(function () {
    return true;
});
```

`skip` 方法可以看作 `when` 的反向操作。如果传给 `skip` 的闭包返回 `true`，调度任务就不会执行：

```php
Schedule::command('emails:send')->daily()->skip(function () {
    return true;
});
```

链式调用多个 `when` 方法时，只有所有 `when` 条件都返回 `true`，调度命令才会执行。

<a name="environment-constraints"></a>
#### 环境约束

`environments` 方法可用于限制任务仅在指定环境中执行，环境由 `APP_ENV` [环境变量](/docs/{{version}}/configuration#environment-configuration) 定义：

```php
Schedule::command('emails:send')
    ->daily()
    ->environments(['staging', 'production']);
```

<a name="timezones"></a>
### 时区

使用 `timezone` 方法，你可以指定调度任务的时间应按哪个时区来解释：

```php
use Illuminate\Support\Facades\Schedule;

Schedule::command('report:generate')
    ->timezone('America/New_York')
    ->at('2:00');
```

如果所有调度任务都需要使用同一时区，你可以在应用程序的 `app` 配置文件中定义 `schedule_timezone` 选项，为所有调度指定该时区：

```php
'timezone' => 'UTC',

'schedule_timezone' => 'America/Chicago',
```

> [!WARNING]
> 请注意，某些时区使用夏令时。夏令时切换时，调度任务可能运行两次，甚至完全不运行。因此，我们建议尽可能避免按时区调度任务。

<a name="preventing-task-overlaps"></a>
### 避免任务重叠

默认情况下，即使任务的上一次执行尚未结束，调度任务仍会运行。若要避免这种情况，可以使用 `withoutOverlapping` 方法：

```php
use Illuminate\Support\Facades\Schedule;

Schedule::command('emails:send')->withoutOverlapping();
```

在此示例中，`emails:send` [Artisan 命令](/docs/{{version}}/artisan) 会每分钟运行一次，前提是它当前没有正在运行的实例。如果任务的执行耗时变化很大，难以准确预测，`withoutOverlapping` 方法就特别有用。

如有需要，你可以指定防重叠锁在多少分钟后过期。默认情况下，锁会在 24 小时后过期：

```php
Schedule::command('emails:send')->withoutOverlapping(10);
```

在底层实现中，`withoutOverlapping` 方法使用应用程序的 [缓存](/docs/{{version}}/cache) 获取锁。必要时，你可以使用 `schedule:clear-cache` Artisan 命令清除这些缓存锁。通常只有在服务器发生意外问题、导致任务卡住时，才需要这样做。

<a name="running-tasks-on-one-server"></a>
### 只在一台服务器上运行任务

> [!WARNING]
> 要使用此功能，应用程序必须将 `database`、`memcached`、`dynamodb` 或 `redis` 作为默认缓存驱动。此外，所有服务器必须连接同一个中央缓存服务器。

如果应用程序的调度器在多台服务器上运行，你可以限制调度作业只在一台服务器上执行。例如，某个任务需要在每周五晚上生成一份新报告。如果调度器在三台工作服务器上运行，该任务就会在三台服务器上分别执行，导致同一报告生成三次。这显然不合适。

要让任务只在一台服务器上运行，请在定义调度任务时使用 `onOneServer` 方法。最先获取该任务的服务器会取得一个原子锁，防止其他服务器同时运行相同任务：

```php
use Illuminate\Support\Facades\Schedule;

Schedule::command('report:generate')
    ->fridays()
    ->at('17:00')
    ->onOneServer();
```

要为所有调度任务应用 `onOneServer`，可以在应用程序的 `AppServiceProvider` 的 `boot` 方法中调用 `alwaysOnOneServer`：

```php
use Illuminate\Support\Facades\Schedule;

public function boot(): void
{
    Schedule::alwaysOnOneServer();
}
```

未指定 [名称](#naming-unique-jobs) 的调度闭包不受此设置影响，仍会在每台服务器上运行。

你可以使用 `useCache` 方法，自定义调度器用于获取单服务器任务所需原子锁的缓存存储：

```php
Schedule::useCache('database');
```

<a name="naming-unique-jobs"></a>
#### 为单服务器作业命名

有时，你可能需要以不同参数调度同一个作业，同时让每种参数组合对应的作业都只在一台服务器上运行。为此，你可以通过 `name` 方法，为每个调度定义指定唯一名称：

```php
Schedule::job(new CheckUptime('https://laravel.com'))
    ->name('check_uptime:laravel.com')
    ->everyFiveMinutes()
    ->onOneServer();

Schedule::job(new CheckUptime('https://vapor.laravel.com'))
    ->name('check_uptime:vapor.laravel.com')
    ->everyFiveMinutes()
    ->onOneServer();
```

同样，如果调度闭包需要只在一台服务器上运行，也必须为其指定名称：

```php
Schedule::call(fn () => User::resetApiRequestCount())
    ->name('reset-api-request-count')
    ->daily()
    ->onOneServer();
```

<a name="background-tasks"></a>
### 后台任务

默认情况下，同一时间安排的多个任务会按照它们在 `schedule` 方法中的定义顺序依次执行。如果某些任务耗时很长，后续任务的启动时间可能比预期晚得多。要让任务在后台运行，以便它们同时执行，可以使用 `runInBackground` 方法：

```php
use Illuminate\Support\Facades\Schedule;

Schedule::command('analytics:report')
    ->daily()
    ->runInBackground();
```

> [!WARNING]
> `runInBackground` 方法仅适用于通过 `command` 和 `exec` 方法调度的任务。

<a name="maintenance-mode"></a>
### 维护模式

应用程序处于 [维护模式](/docs/{{version}}/configuration#maintenance-mode) 时，调度任务不会运行，以免干扰服务器上尚未完成的维护操作。不过，如果你希望某个任务在维护模式下仍强制运行，可以在定义任务时调用 `evenInMaintenanceMode` 方法：

```php
Schedule::command('emails:send')->evenInMaintenanceMode();
```

<a name="pausing-scheduled-tasks"></a>
### 暂停调度任务

你可以使用 `schedule:pause` Artisan 命令，临时暂停调度任务处理，无需修改已部署的代码：

```shell
php artisan schedule:pause
```

调度器暂停期间，不会运行任何调度任务。你可以使用 `schedule:continue` 命令恢复调度任务处理：

```shell
php artisan schedule:continue
```

如果某个任务在调度器暂停期间仍应运行，可以使用 `evenWhenPaused` 方法标记该任务：

```php
Schedule::command('emails:send')->evenWhenPaused();
```

<a name="schedule-groups"></a>
### 调度分组

定义多个配置相似的调度任务时，你可以使用 Laravel 的任务分组功能，避免为每个任务重复相同设置。任务分组可以简化代码，并确保相关任务的配置一致。

要创建一组调度任务，请先调用所需的任务配置方法，再调用 `group` 方法。`group` 方法接受一个闭包，用于定义共享这些配置的任务：

```php
use Illuminate\Support\Facades\Schedule;

Schedule::daily()
    ->onOneServer()
    ->timezone('America/New_York')
    ->group(function () {
        Schedule::command('emails:send --force');
        Schedule::command('emails:prune');
    });
```

<a name="running-the-scheduler"></a>
## 运行调度器

了解如何定义调度任务后，接下来看看如何在服务器上实际运行它们。`schedule:run` Artisan 命令会检查所有调度任务，并根据服务器当前时间判断哪些任务需要执行。

因此，使用 Laravel 调度器时，只需在服务器上添加一条 cron 配置，让它每分钟运行一次 `schedule:run` 命令。如果你不知道如何添加 cron 条目，可以考虑使用 [Laravel Cloud](https://cloud.laravel.com) 等托管平台，由平台为你管理调度任务的执行：

```shell
* * * * * cd /path-to-your-project && php artisan schedule:run >> /dev/null 2>&1
```

<a name="sub-minute-scheduled-tasks"></a>
### 亚分钟级调度任务

在大多数操作系统中，cron 任务最多每分钟运行一次。不过，Laravel 调度器允许你以更短的时间间隔运行任务，甚至每秒运行一次：

```php
use Illuminate\Support\Facades\Schedule;

Schedule::call(function () {
    DB::table('recent_users')->delete();
})->everySecond();
```

当应用程序中定义了亚分钟级任务时，`schedule:run` 命令会持续运行到当前分钟结束，而非立即退出，从而在这一分钟内调用所有需要执行的亚分钟级任务。

如果亚分钟级任务的执行时间超过预期，就可能延迟后续亚分钟级任务的执行。因此，建议所有亚分钟级任务都通过分发队列作业或后台命令来处理实际的任务逻辑：

```php
use App\Jobs\DeleteRecentUsers;

Schedule::job(new DeleteRecentUsers)->everyTenSeconds();

Schedule::command('users:delete')->everyTenSeconds()->runInBackground();
```

<a name="interrupting-sub-minute-tasks"></a>
#### 中断亚分钟级任务

定义了亚分钟级任务后，`schedule:run` 命令会持续运行到调用它的当前分钟结束，因此在部署应用程序时，有时需要中断该命令。否则，正在运行的 `schedule:run` 实例会继续使用部署前的应用程序代码，直到当前分钟结束。

要中断正在运行的 `schedule:run`，你可以在应用程序的部署脚本中添加 `schedule:interrupt` 命令。该命令应在应用程序部署完成后执行：

```shell
php artisan schedule:interrupt
```

<a name="running-the-scheduler-locally"></a>
### 在本地运行调度器

通常，你无需在本地开发机器上为调度器添加 cron 配置，而是可以使用 `schedule:work` Artisan 命令。该命令会在前台运行，每分钟调用一次调度器，直到你终止它。如果定义了亚分钟级任务，调度器会在每分钟内持续运行，以处理这些任务：

```shell
php artisan schedule:work
```

<a name="task-output"></a>
## 任务输出

Laravel 调度器提供了多种便捷方法，用于处理调度任务产生的输出。首先，你可以使用 `sendOutputTo` 方法，将输出写入文件，供后续查看：

```php
use Illuminate\Support\Facades\Schedule;

Schedule::command('emails:send')
    ->daily()
    ->sendOutputTo($filePath);
```

如果希望将输出追加到指定文件，可以使用 `appendOutputTo` 方法：

```php
Schedule::command('emails:send')
    ->daily()
    ->appendOutputTo($filePath);
```

使用 `emailOutputTo` 方法，你可以将输出通过邮件发送到指定地址。在发送任务输出之前，请先配置 Laravel 的 [邮件服务](/docs/{{version}}/mail)：

```php
Schedule::command('report:generate')
    ->daily()
    ->sendOutputTo($filePath)
    ->emailOutputTo('taylor@example.com');
```

如果你只希望在调度的 Artisan 命令或系统命令以非零退出码结束时，通过邮件发送输出，可以使用 `emailOutputOnFailure` 方法：

```php
Schedule::command('report:generate')
    ->daily()
    ->emailOutputOnFailure('taylor@example.com');
```

> [!WARNING]
> `emailOutputTo`、`emailOutputOnFailure`、`sendOutputTo` 和 `appendOutputTo` 方法仅适用于通过 `command` 和 `exec` 方法调度的任务。

<a name="task-hooks"></a>
## 任务钩子

使用 `before` 和 `after` 方法，你可以指定在调度任务执行前后运行的代码：

```php
use Illuminate\Support\Facades\Schedule;

Schedule::command('emails:send')
    ->daily()
    ->before(function () {
        // 任务即将执行...
    })
    ->after(function () {
        // 任务已执行...
    });
```

`onSuccess` 和 `onFailure` 方法允许你指定在调度任务成功或失败时运行的代码。失败表示调度的 Artisan 命令或系统命令以非零退出码结束：

```php
Schedule::command('emails:send')
    ->daily()
    ->onSuccess(function () {
        // 任务执行成功...
    })
    ->onFailure(function () {
        // 任务执行失败...
    });
```

如果命令产生了输出，你可以在 `after`、`onSuccess` 或 `onFailure` 钩子中访问它。只需在钩子闭包定义中，为 `$output` 参数添加 `Illuminate\Support\Stringable` 类型声明：

```php
use Illuminate\Support\Stringable;

Schedule::command('emails:send')
    ->daily()
    ->onSuccess(function (Stringable $output) {
        // 任务执行成功...
    })
    ->onFailure(function (Stringable $output) {
        // 任务执行失败...
    });
```

<a name="pinging-urls"></a>
#### 向 URL 发送通知

使用 `pingBefore` 和 `thenPing` 方法，调度器可以在任务执行前或执行后，自动向指定 URL 发送请求。这适合用于通知 [Envoyer](https://envoyer.io) 等外部服务，告知调度任务即将开始或已执行完毕：

```php
Schedule::command('emails:send')
    ->daily()
    ->pingBefore($url)
    ->thenPing($url);
```

`pingOnSuccess` 和 `pingOnFailure` 方法可用于仅在任务成功或失败时向指定 URL 发送请求。失败表示调度的 Artisan 命令或系统命令以非零退出码结束：

```php
Schedule::command('emails:send')
    ->daily()
    ->pingOnSuccess($successUrl)
    ->pingOnFailure($failureUrl);
```

`pingBeforeIf`、`thenPingIf`、`pingOnSuccessIf` 和 `pingOnFailureIf` 方法可用于仅在给定条件为 `true` 时向指定 URL 发送请求：

```php
Schedule::command('emails:send')
    ->daily()
    ->pingBeforeIf($condition, $url)
    ->thenPingIf($condition, $url);

Schedule::command('emails:send')
    ->daily()
    ->pingOnSuccessIf($condition, $successUrl)
    ->pingOnFailureIf($condition, $failureUrl);
```

<a name="events"></a>
## 事件

Laravel 会在调度过程中分发多种 [事件](/docs/{{version}}/events)。你可以为以下任意事件 [定义监听器](/docs/{{version}}/events)：

<div class="overflow-auto" markdown="1">

| 事件名称                                                  |
| ----------------------------------------------------------- |
| `Illuminate\Console\Events\ScheduledTaskStarting`           |
| `Illuminate\Console\Events\ScheduledTaskFinished`           |
| `Illuminate\Console\Events\ScheduledBackgroundTaskFinished` |
| `Illuminate\Console\Events\ScheduledTaskSkipped`            |
| `Illuminate\Console\Events\ScheduledTaskFailed`             |

</div>
