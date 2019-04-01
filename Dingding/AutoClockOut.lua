require "TSLib"

--解锁屏幕
flag = deviceIsLock(); 
if flag ~= 0 then
	unlockDevice();    
end

--开启wifi
--setWifiEnable(true);
--toast("开启wifi", 3);
--mSleep(20000);

interval_sleep_time = 10000 --ms


--返回桌面并打开钉钉
pressHomeKey();
mSleep(interval_sleep_time)
if multiColor({{  513, 1173, 0xffffff}}) == true then
	tap(513, 1173)
	mSleep(interval_sleep_time)
else
	lua_exit() -- 避免点到其他东西
end

--点击工作栏
tap(360, 1226)
mSleep(interval_sleep_time)
moveTo(662,  300, 667, 1000) -- 滑动到顶

	
--点击考勤打卡
if multiColor({{386, 1222, 0x36aefc}, {360, 1250, 0x36affe}}) == true then
	tap(270,  983)
	mSleep(interval_sleep_time)
else
	lua_exit() -- 避免点到其他东西
end


if multiColor({{268,  501, 0x22a3fe}, {460,  501, 0x22a3fe}}) == true or multiColor({{272,  497, 0x25a5fe}, {451,  500, 0x25a5fe}}) == true then
	toast("上班打卡",1)
	tap(358,  490)
	mSleep(interval_sleep_time)
else
	toast("下班打卡",1)
	moveTo(667, 1170, 662,  1) -- 滑动到底，从下往上找圆圈
	x, y = 140, 1160
	while y >= 0 and isColor(x, y, 0x39ca49) == false do
		y = y - 2
	end

	if y >= 0 then
		tap(x + 200,   y-200)
	else -- 更新打卡
		toast("找不到正常打卡圆圈, 更新打卡", 3);
		tap(253,  787)
		tap(120,  787)
		mSleep(interval_sleep_time)
		tap(565,  712)
		mSleep(interval_sleep_time)
	end

	-- 早退打卡
	if multiColor({{  499, 1043, 0x3da9f2},{  546, 1043, 0x40a8ef}}) == true then
		tap(499, 1043)
		toast("早退打卡", 3);
		mSleep(interval_sleep_time)
	end
end

-- 点击“我知道了” 并返回主界面
tap(499, 1018)
mSleep(interval_sleep_time)
tap(40,   98)
mSleep(interval_sleep_time)


-- 关闭wifi
--setWifiEnable(false);
--toast("关闭wifi", 3);

lockDevice(); --锁定屏幕
lua_exit();