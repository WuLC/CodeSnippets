--Created on Sat Dec 22 2018 19:9:35
--Author: WuLC
--EMail: liangchaowu5@gmail.com

require "TSLib"

--解锁屏幕
flag = deviceIsLock(); 
if flag ~= 0 then
	unlockDevice();    
end

--开启wifi
setWifiEnable(true);
toast("开启wifi", 3);
mSleep(20000);

--点击工作栏
tap(360, 1226)
mSleep(1000)

-- 滑动到顶并点击考勤打卡
moveTo(662,  300, 667, 1000)
if multiColor({{   386, 1222, 0x36aefc},{   360, 1250, 0x36affe}}) == true then
	tap(270,  983)
	mSleep(10000) -- 加载时间较长
end

-- 点击打卡圆圈(如果有)
moveTo(667, 1170, 662,  1) -- 滑动到底，从下往上找圆圈
x, y = 140, 1160
while y >= 0 and isColor(x, y, 0x39ca49) == false do
	y = y - 2
end

if y >= 0 then
	tap(x + 200,   y-200)
else -- 更新打卡
	toast("找不到圆圈, 更新打卡", 3);
	tap(253,  787)
	mSleep(5000)
	tap(565,  712)
	mSleep(4000)
end


-- 早退打卡
if multiColor({{  499, 1043, 0x3da9f2},{  546, 1043, 0x40a8ef}}) == true then
	tap(499, 1043)
	mSleep(5000)
end

-- 点击“我知道了” 并返回主界面
if multiColor({{  301, 1018, 0x2e8fee},{  388, 1022, 0x3392ee}}) == true then
	tap(301, 1018)
	tap(40,   98)
	mSleep(4000)
end


-- 关闭wifi, 锁定屏幕并退出
setWifiEnable(false);
toast("关闭wifi", 3);
lockDevice(); 
lua_exit();