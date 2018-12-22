require "TSLib"

--解锁屏幕
flag = deviceIsLock(); 
if flag ~= 0 then
	unlockDevice();    
end

--点击工作栏
if multiColor({{   386, 1222, 0x36aefc},{   360, 1250, 0x36affe}}) == false then 
	tap(360, 1226)
end

mSleep(1000)

--点击考勤打卡
if multiColor({{   386, 1222, 0x36aefc},{   360, 1250, 0x36affe}}) == true then
	tap(270,  983)
end

mSleep(10000)

-- 点击打卡圆圈
moveTo(667, 1170, 662,  1) -- 滑动到底，从下往上找圆圈
moveTo(667, 1170, 662,  1) -- 滑动到底，从下往上找圆圈
x, y = 140, 1160
while isColor(x, y, 0x39ca49) == false do
	y = y - 2
end

tap(x + 200,   y-200)

mSleep(4000)

-- 点击“我知道了” 并返回主界面
if multiColor({{  355,  451, 0xffffff},{  357,  430, 0x3096f8}}) == true then
	tap(359, 1022)
	tap(40,   98)
end

mSleep(4000)
lockDevice(); --锁定屏幕
lua_exit();