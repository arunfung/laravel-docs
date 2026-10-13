# 任务调度

- [介绍](#introduction)
- [定义调度](#defining-schedules)
    - [调度 Artisan 命令](#scheduling-artisan-commands)
    - [调度队列作业](#scheduling-queued-jobs)
    - [调度 Shell 命令](#scheduling-shell-commands)
    - [调度频率选项](#schedule-frequency-options)
    - [时区](#timezones)
    - [避免任务重复](#preventing-task-overlaps)
    - [只在一台服务器上运行任务](#running-tasks-on-one-server)
    - [后台任务](#background-tasks)
    - [维护模式](#maintenance-mode)
    - [调度组](#schedule-groups)
- [运行调度器](#running-the-scheduler)
    - [少于一分钟的计划任务](#sub-minute-scheduled-tasks)
    - [本地运行调度器](#running-the-scheduler-locally)
- [任务输出](#task-output)
- [任务钩子](#task-hooks)
- [事件](#events)

<a name="introduction"></a>
## 简介

过去，你可能需要在服务器上为每一个调度任务去创建一个 cron 配置项。但是，这种方式很快会变得麻烦，因为你的任务调度已不在源代码控制中，而且你必须通过 SSH 登录到服务器才能查看现有的 cron 配置项或添加其他配置项。

Laravel 的命令调度器提供了一种全新的方法来管理服务器上的定时任务。调度器允许你在 Laravel 应用中流畅且直观地定义命令调度。使用调度器时，服务器上只需要一个单一的 cron 配置项。你的任务调度通常在应用程序的 `routes/console.php` 文件中定义。

<a name="defining-schedules"></a>
## 定义调度

你可以在应用程序的 `routes/console.php`文件中定义所有计划任务。首先，我们来看一个示例。在此示例中，我们将调度一个闭包，使其每天午夜执行。在闭包中，我们将执行一个数据库查询来清空表：

```php
<?php

use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schedule;

Schedule::call(function () {
    DB::table('recent_users')->delete();
})->daily();
```



除了使用闭包进行调度外，你还可以调度[invokable 对象](https://secure.php.net/manual/en/language.oop5.magic.php#object.invoke)。invokable 对象是包含`__invoke`方法的简单 PHP 类:

```php
Schedule::call(new DeleteRecentUsers)->daily();
```

如果你倾向于仅将`routes/console.php`文件用于命令定义，那么可以在应用程序的`bootstrap/app.php`文件中使用`withSchedule`方法来定义计划任务。该方法接受一个闭包，此闭包会接收调度器的一个实例：

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

除了调度闭包，你还可以调度 Artisan 命令 和系统命令。例如，你可以使用`command`方法通过命令名称或类来调度 Artisan 命令。

当使用命令的类名来调度 Artisan 命令时，你可以传递一个额外的命令行参数数组，这些参数会在命令被调用时提供给该命令：

```php
use App\Console\Commands\SendEmailsCommand;
use Illuminate\Support\Facades\Schedule;

Schedule::command('emails:send Taylor --force')->daily();

Schedule::command(SendEmailsCommand::class, ['Taylor', '--force'])->daily();
```

<a name="scheduling-artisan-closure-commands"></a>
#### 调度 Artisan 闭包命令

如果你想调度一个由闭包定义的 Artisan 命令，可以在命令定义后链式调用与调度相关的方法：

```php
Artisan::command('delete:recent-users', function () {
    DB::table('recent_users')->delete();
})->purpose('Delete recent users')->daily();
```



如果你需要向闭包命令传递参数，可以将参数提供给 `schedule` 方法：

```php
Artisan::command('emails:send {user} {--force}', function ($user) {
    // ...
})->purpose('Send emails to the specified user')->schedule(['Taylor', '--force'])->daily();
```

<a name="scheduling-queued-jobs"></a>
### 调度队列作业

`job` 方法可用于调度[队列作业](/docs/laravel/12.x/queues)。该方法提供了一种便捷方式来调度队列作业，而无需使用 `call` 方法定义闭包来将作业加入队列：

```php
use App\Jobs\Heartbeat;
use Illuminate\Support\Facades\Schedule;

Schedule::job(new Heartbeat)->everyFiveMinutes();
```

可以向 `job` 方法提供可选的第二个和第三个参数，它们分别指定应使用的队列名称和队列连接，用于将作业加入队列：

```php
use App\Jobs\Heartbeat;
use Illuminate\Support\Facades\Schedule;

// 将作业分发到 「sqs」连接上的「heartbeats」队列...
Schedule::job(new Heartbeat, 'heartbeats', 'sqs')->everyFiveMinutes();
```

<a name="scheduling-shell-commands"></a>
### 调度 Shell 命令

`exec` 方法可用于向操作系统发出命令：

```php
use Illuminate\Support\Facades\Schedule;

Schedule::exec('node /home/forge/script.js')->daily();
```

<a name="schedule-frequency-options"></a>
### 调度频率选项

我们已经举例说明了如何配置任务在指定的时间间隔内运行。然而，你还可以为任务分配更多的任务调度频率：

<div class="overflow-auto">

| 方法    | 描述       |
| ------------------- | ----------------- |
| `->cron('* * * * *');`             | 按自定义 Cron 计划运行任务。 |
| `->everySecond();`                 | 每秒运行一次任务。 |
| `->everyTwoSeconds();`             | 每 2 秒运行一次任务。|
| `->everyFiveSeconds();`            | 每 5 秒运行一次任务。 |
| `->everyTenSeconds();`             | 每 10 秒运行一次任务。|
| `->everyFifteenSeconds();`         | 每 15 秒运行一次任务。|
| `->everyTwentySeconds();`          | 每 20 秒运行一次任务。|
| `->everyThirtySeconds();`          | 每 30 秒运行一次任务。|
| `->everyMinute();`                 | 每分钟运行一次任务。 |
| `->everyTwoMinutes();`             | 每 2 分钟运行一次任务。|
| `->everyThreeMinutes();`           | 每 3 分钟运行一次任务。|
| `->everyFourMinutes();`            | 每 4 分钟运行一次任务。|
| `->everyFiveMinutes();`            | 每 5 分钟运行一次任务。|
| `->everyTenMinutes();`             | 每 10 分钟运行一次任务。|
| `->everyFifteenMinutes();`         | 每 15 分钟运行一次任务。|
| `->everyThirtyMinutes();`          | 每 30 分钟运行一次任务。|
| `->hourly();`                      | 每小时运行一次任务。|
| `->hourlyAt(17);`                  | 每小时的 17 分钟时运行一次任务。|
| `->everyOddHour($minutes = 0);`    | 每奇数小时运行一次任务。|
| `->everyTwoHours($minutes = 0);`   | 每 2 小时运行一次任务。|
| `->everyThreeHours($minutes = 0);` | 每 3 小时运行一次任务。|
| `->everyFourHours($minutes = 0);`  | 每 4 小时运行一次任务。|
| `->everySixHours($minutes = 0);`   | 每 6 小时运行一次任务。|
| `->daily();`                       | 每天午夜 12 点（00:00）运行一次任务。|
| `->dailyAt('13:00');`              | 每天 13:00 运行一次任务。|
| `->twiceDaily(1, 13);`             | 每天在 1:00 和 13:00 运行一次任务。 |
| `->twiceDailyAt(1, 13, 15);`       | 每天在 1:15 和 13:15 运行一次任务。 |
| `->weekly();`                      | 每周日 00:00 运行一次任务。|
| `->weeklyOn(1, '8:00');`           | 每周一 8:00 运行一次任务。|
| `->monthly();`                     | 每月第一天 00:00 运行一次任务。|
| `->monthlyOn(4, '15:00');`         | 每月 4 日 15:00 运行一次任务。            |
| `->twiceMonthly(1, 16, '13:00');`  | 每月 1 日和 16 日 13:00 运行一次任务。   |
| `->lastDayOfMonth('15:00');`       | 每月最后一天 15:00 运行一次任务。    |
| `->quarterly();`                   | 每个季度的第一天 00:00 运行一次任务。 |
| `->quarterlyOn(4, '14:00');`       | 每个季度的第 4 天 14:00 运行一次任务。|
| `->yearly();`                      | 每年的第一天 00:00 运行一次任务。     |
| `->yearlyOn(6, 1, '17:00');`       | 每年 6 月 1 日 17:00 运行一次任务。   |
| `->timezone('America/New_York');`  | 设置任务时区。                       |

</div>


这些方法可以与其他约束条件结合使用，从而创建出更精细的调度，使其仅在一周中的特定日期运行。例如，你可以将命令安排为每周一运行：

```php
use Illuminate\Support\Facades\Schedule;

// 每周运行一次，时间为周一下午 1 点...
Schedule::call(function () {
    // ...
})->weekly()->mondays()->at('13:00');

// 在工作日上午 8 点至下午 5 点之间，每小时运行一次...
Schedule::command('foo')
    ->weekdays()
    ->hourly()
    ->timezone('America/Chicago')
    ->between('8:00', '17:00');
```

其他调度约束条件列表如下：
<div class="overflow-auto">

| 方法 | 描述  |
| ----------------------- | ------------------------------------ |
| `->weekdays();`                          | 将任务限制为工作日。 |
| `->weekends();`                          | 将任务限制到周末。 |
| `->sundays();`                           | 将任务限制到周日。 |
| `->mondays();`                           | 将任务限制在周一。|
| `->tuesdays();`                          | 将任务限制在周二。|
| `->wednesdays();`                        | 将任务限制在周三。|
| `->thursdays();`                         | 将任务限制在周四。|
| `->fridays();`                           | 将任务限制在周五。|
| `->saturdays();`                         | 将任务限制在周六。|
| `->days(array\|mixed);`                  | 将任务限制在特定日期。|
| `->between($startTime, $endTime);`       | 限制任务在开始时间和结束时间之间运行。|
| `->unlessBetween($startTime, $endTime);` | 限制任务不在开始时间和结束时间之间运行。|
| `->when(Closure);`                       | 根据真值测试限制任务。|
| `->environments($env);`                  | 将任务限制在特定环境中。|

</div>

<a name="day-constraints"></a>
#### 日约束

`days` 方法可以用于约束任务在每周的指定日期执行。例如，你可以调度命令在周日和周三每小时运行一次：

```php
use Illuminate\Support\Facades\Schedule;

Schedule::command('emails:send')
    ->hourly()
    ->days([0, 3]);
```


不仅如此，在定义任务应运行的日期时，你可以使用 `Illuminate\Console\Scheduling\Schedule` 类上可用的常量：

```php
use Illuminate\Support\Facades;
use Illuminate\Console\Scheduling\Schedule;

Facades\Schedule::command('emails:send')
    ->hourly()
    ->days([Schedule::SUNDAY, Schedule::WEDNESDAY]);
```

<a name="between-time-constraints"></a>
#### 时间区间约束

`between` 方法可用于限制任务在一天中的某个时间段执行：

```php
Schedule::command('emails:send')
    ->hourly()
    ->between('7:00', '22:00');
```

同样，`unlessBetween` 方法也可用于限制任务不在一天中的某个时间段执行：

```php
Schedule::command('emails:send')
    ->hourly()
    ->unlessBetween('23:00', '4:00');
```

<a name="truth-test-constraints"></a>
#### 真值检测约束

`when` 方法可根据闭包返回结果来执行任务。换句话说，如果给定的闭包返回 `true`，则只要没有其他约束条件阻止任务运行，该任务就会执行：

```php
Schedule::command('emails:send')->daily()->when(function () {
    return true;
});
```

`skip` 方法可看作是 `when` 的逆方法。若 `skip` 方法返回 `true`，任务将不会执行：

```php
Schedule::command('emails:send')->daily()->skip(function () {
    return true;
});
```

当链式调用 `when` 方法时，仅当所有 `when` 都返回 `true` 时，已调度的命令才会执行。

<a name="environment-constraints"></a>
#### 环境约束

`environments` 方法可用于指定任务的执行环境（由 `APP_ENV` [环境变量](/docs/laravel/12.x/configuration#environment-configuration)定义)：

```php
Schedule::command('emails:send')
    ->daily()
    ->environments(['staging', 'production']);
```



<a name="timezones"></a>
### 时区

使用 `timezone` 方法，方法，你可以指定计划任务的时间转化为给定的时区：

```php
use Illuminate\Support\Facades\Schedule;

Schedule::command('report:generate')
    ->timezone('America/New_York')
    ->at('2:00')
```

如果你需要为所有计划任务重复分配相同时区，你可以通过在应用程序的 `app` 配置文件中定义 `schedule_timezone` 选项来指定应分配给所有计划任务的时区：

```php
'timezone' => 'UTC',

'schedule_timezone' => 'America/Chicago',
```

> [!WARNING]
> 请记住，有些时区使用夏令时。当夏令时发生变化时，你的计划任务可能会运行两次，甚至根本不会运行。因此，我们建议尽可能避免时区调度。

<a name="preventing-task-overlaps"></a>
### 避免任务重复

默认情况下，即使任务的前一个实例仍在运行，计划任务仍会执行。若要防止这种情况，可以使用 `withoutOverlapping` 方法：

```php
use Illuminate\Support\Facades\Schedule;

Schedule::command('emails:send')->withoutOverlapping();
```

在此例中，若 `emails:send` [Artisan 命令](/docs/laravel/12.x/artisan) 尚未运行，则它将会每分钟执行一次。如果任务的执行时间非常不确定，导致你无法准确预测任务的执行时间，那么 `withoutOverlapping` 方法就特别有用。

如果需要，你可以在「without overlapping」 锁过期之前，指定它的过期分钟数。默认情况下，这个锁会在 24 小时后过期：

```php
Schedule::command('emails:send')->withoutOverlapping(10);
```

在底层实现中，`withoutOverlapping` 方法使用应用程序的 [cache](/docs/laravel/12.x/cache) 来获取锁。如果必要，你可以使用 `schedule:clear-cache` Artisan 命令清除这些缓存锁。通常只有在服务器出现意外问题导致任务卡住时才需要这样做。

<a name="running-tasks-on-one-server"></a>
### 只在一台服务器上运行任务

> [!WARNING]
> 要使用此功能，你的应用程序必须将 `database` ， `memcached` ， `dynamodb` ，或 `redis` 缓存驱动程序用作应用程序的默认缓存驱动程序。此外，所有服务器必须与同一中央缓存服务器进行通信。

如果你的应用程序的调度器在多台服务器上运行，你可以限制计划任务只在一台服务器上执行。例如，假设你有一个计划任务，每周五晚上生成一份新报告。如果任务调度器在三个工作服务器上运行，则计划任务将在所有三个服务器上运行并三次生成报告。这不好！

要表示任务仅在一台服务器上运行，请在定义计划任务时使用 `onOneServer` 方法。第一个获得任务的服务器将确保任务的原子锁，以防止其他服务器同时运行同一任务：

```php
use Illuminate\Support\Facades\Schedule;

Schedule::command('report:generate')
    ->fridays()
    ->at('17:00')
    ->onOneServer();
```

你可以使用 `useCache` 方法来自定义调度器用于获取单服务器任务所需原子锁的缓存存储：

```php
Schedule::useCache('database');
```

<a name="naming-unique-jobs"></a>
#### 为单服务器任务命名

有时你可能需要调度同一作业并为其分配不同的参数，同时仍要指示 Laravel 在单台服务器上运行该作业的每个排列。要实现这一点，你可以通过 `name` 方法为每个调度定义分配一个唯一的名称：

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

同样，如果打算在一台服务器上运行计划闭包，则必须为其分配一个名称：

```php
Schedule::call(fn () => User::resetApiRequestCount())
    ->name('reset-api-request-count')
    ->daily()
    ->onOneServer();
```

<a name="background-tasks"></a>
### 后台任务

默认情况下，同一时间调度的多个任务会根据其在 `schedule` 方法中的定义顺序依次执行。如果存在长时间运行的任务，这可能导致后续任务的启动时间比预期晚很多。如果你想在后台运行任务，以便它们同时运行，你可以使用 `runInBackground` 方法：

```php
use Illuminate\Support\Facades\Schedule;

Schedule::command('analytics:report')
    ->daily()
    ->runInBackground();
```

> [!WARNING]
> `runInBackground` 方法只能在通过 `command` 和 `exec` 方法调度任务时使用。

<a name="maintenance-mode"></a>
### 维护模式

当应用程序处于[维护模式](/docs/laravel/12.x/configuration#maintenance-mode)时，你的应用程序计划任务将不会运行，因为我们不想调度任务干扰到服务器上可能还未完成的维护项目。然而，如果你想强制任务在维护模式下运行，你可以使用 `evenInMaintenanceMode` 方法：

```php
Schedule::command('emails:send')->evenInMaintenanceMode();
```

<a name="schedule-groups"></a>
### 调度分组

当定义多个具有相似配置的计划任务时，你可以使用 Laravel 的任务分组功能，避免为每个任务重复设置相同的配置。任务分组不仅简化了代码，还能确保相关任务的配置保持一致。

若要创建一组计划任务，需先调用所需的任务配置方法，然后再调用 `group` 方法。`group` 方法接受一个闭包，该闭包负责定义共享指定配置的任务：

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

现在我们已经了解了如何定义计划任务，接下来讨论如何在服务器上实际运行这些任务。`schedule:run` Artisan 命令会评估所有计划任务，并根据服务器的当前时间判断它们是否需要运行。

因此，使用 Laravel 调度器时，只需在服务器的 cron 配置中添加一条每分钟执行 `schedule:run` 命令的条目即可。如果您不知道如何在服务器上添加 cron 条目，可以考虑使用 [Laravel Cloud](https://cloud.laravel.com) 等托管平台，它能为您管理计划任务的执行：

```shell
* * * * * cd /path-to-your-project && php artisan schedule:run >> /dev/null 2>&1
```

<a name="sub-minute-scheduled-tasks"></a>
### 中断亚分钟任务

在大多数操作系统中，cron 作业最多每分钟运行一次。然而，Laravel 的调度器允许你将任务安排为更频繁的间隔执行，甚至可以每秒运行一次：

```php
use Illuminate\Support\Facades\Schedule;

Schedule::call(function () {
    DB::table('recent_users')->delete();
})->everySecond();
```



当应用程序中定义了亚分钟级任务时，`schedule:run` 命令会持续运行至当前分钟结束，而非立即退出。这样可确保该命令在整分钟内调用所有需要执行的亚分钟级任务。

由于运行时间超过预期的亚分钟级任务可能会延迟后续亚分钟级任务的执行，因此建议所有亚分钟级任务都通过分发队列作业或后台命令来处理实际的任务逻辑：

```php
use App\Jobs\DeleteRecentUsers;

Schedule::job(new DeleteRecentUsers)->everyTenSeconds();

Schedule::command('users:delete')->everyTenSeconds()->runInBackground();
```

<a name="interrupting-sub-minute-tasks"></a>
#### 中断亚分钟任务

由于在定义了亚分钟任务时，`schedule:run` 命令会在调用的整分钟内运行，因此有时可能需要在部署应用程序时中断该命令。否则，已在运行的 `schedule:run` 命令实例将继续使用你的应用程序先前部署的代码，直到当前分钟结束。

为了中断正在进行的 `schedule:run` 调用，你可添加 `schedule:interrupt` 命令到应用程序的部署脚本中。该命令应在你的应用程序部署完成后调用：

```shell
php artisan schedule:interrupt
```

<a name="running-the-scheduler-locally"></a>
### 本地运行调度器

通常，你不会在本地开发机器上添加调度器 cron 条目。相反，你可以使用 `schedule:work` Artisan 命令。该命令会在前台运行，并每分钟触发一次调度器，直到你手动终止该命令。当定义了亚分钟级任务时，调度器会在每分钟内持续运行以处理这些任务：

```shell
php artisan schedule:work
```

<a name="task-output"></a>
## 任务输出

Laravel 调度器提供了多种便捷方法来处理计划任务生成的输出。首先，使用 `sendOutputTo` 方法可以将输出发送到文件以便后续检查：

```php
use Illuminate\Support\Facades\Schedule;

Schedule::command('emails:send')
    ->daily()
    ->sendOutputTo($filePath);
```

如果你希望将输出追加到给定文件，你可以使用 `appendOutputTo` 方法：

```php
Schedule::command('emails:send')
    ->daily()
    ->appendOutputTo($filePath);
```

使用 `emailOutputTo` 方法，你可以把输出结果电邮到你选择的电邮地址。在发送任务的输出结果之前，你应该配置 Laravel 的[电子邮件服务](/docs/laravel/12.x/mail):

```php
Schedule::command('report:generate')
    ->daily()
    ->sendOutputTo($filePath)
    ->emailOutputTo('taylor@example.com');
```

如果你只希望在计划的 Artisan 或系统命令以非零退出码终止时通过电子邮件发送输出，可以使用 `emailOutputOnFailure` 方法：

```php
Schedule::command('report:generate')
    ->daily()
    ->emailOutputOnFailure('taylor@example.com');
```

> [!WARNING]
> `emailOutputTo` ， `emailOutputOnFailure` ， `sendOutputTo` 和 `appendOutputTo` 方法仅适用于 `command` 和 `exec` 方法。

<a name="task-hooks"></a>
## 任务钩子

使用 `before` 和 `after` 方法，你可以指定在计划任务执行前后要执行的代码：

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

`onSuccess` 和 `onFailure` 方法允许你指定在计划任务成功或失败时执行的代码。失败表示预定的 Artisan 或系统命令以非零的退出代码终止：

```php
Schedule::command('emails:send')
    ->daily()
    ->onSuccess(function () {
        // 任务成功...
    })
    ->onFailure(function () {
        // 任务失败...
    });
```



如果命令中提供了输出，你可以在 `after`、`onSuccess` 或 `onFailure` 钩子中访问这些输出。具体方法是在钩子闭包的定义中，将 `$output` 参数类型提示为 `Illuminate\Support\Stringable` 实例：

```php
use Illuminate\Support\Stringable;

Schedule::command('emails:send')
    ->daily()
    ->onSuccess(function (Stringable $output) {
        // 任务成功...
    })
    ->onFailure(function (Stringable $output) {
        // 任务失败...
    });
```

<a name="pinging-urls"></a>
#### URL ping 检测

使用 `pingBefore` 和 `thenPing` 方法，调度器可以在任务执行前或执行后自动 ping 一个指定的 URL。此功能对于通知外部服务（如 [Envoyer](https://envoyer.io)）你的计划任务即将开始或已完成执行特别有用：

```php
Schedule::command('emails:send')
    ->daily()
    ->pingBefore($url)
    ->thenPing($url);
```

`pingOnSuccess` 和 `pingOnFailure` 方法可用于仅在任务成功或失败时 ping 指定的 URL。失败表示计划的 Artisan 或系统命令以非零退出码终止：

```php
Schedule::command('emails:send')
    ->daily()
    ->pingOnSuccess($successUrl)
    ->pingOnFailure($failureUrl);
```

`pingBeforeIf`、`thenPingIf`、`pingOnSuccessIf` 和 `pingOnFailureIf` 方法可用于仅在给定条件为 `true` 时 ping 指定的 URL：

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

Laravel 在调度过程中发送各种[事件](https://learnku.com/docs/laravel/11.x/events)。你可以为以下事件[定义监听器](https://learnku.com/docs/laravel/11.x/events)：

<div class="overflow-auto">

| 事件名 |
| --- |
| `Illuminate\Console\Events\ScheduledTaskStarting` |
| `Illuminate\Console\Events\ScheduledTaskFinished` |
| `Illuminate\Console\Events\ScheduledBackgroundTaskFinished` |
| `Illuminate\Console\Events\ScheduledTaskSkipped` |
| `Illuminate\Console\Events\ScheduledTaskFailed` |

</div>
