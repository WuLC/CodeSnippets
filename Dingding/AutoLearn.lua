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


--返回桌面并打开app
pressHomeKey();
toast("返回桌面", 3);
mSleep(2000)

if multiColor({{  219, 1145, 0xd20200}}) == true then
	tap(219, 1145)
	mSleep(10000)
	tap(42,  112) -- 返回
else
	lua_exit() -- 避免点到其他东西
end

-------------------------------------------------
-- 点击文章栏，恢复频道栏，并分别点击四个频道
-- 每个频道浏览三篇文章
-------------------------------------------------
interval_sleep_time = 10000  -- time between clicks
passage_sleep_time = 30000
tap(362, 1215)
for i=1, 3 do
	moveTo(27,  190, 701,  192)
end

channels = {38,179,  181,189,  289,191,  421,186}
passages = {493,677,  529,921,  526,1087}
for i= 1, 4 do
	tap(channels[i*2-1],  channels[i*2])
	mSleep(interval_sleep_time)
	for j=1, 3 do
		tap(passages[j*2-1], passages[j*2])
		mSleep(passage_sleep_time)
		moveTo(667, 1170, 662,  150)
		moveTo(667, 1170, 662,  150)
		mSleep(passage_sleep_time)
		tap(42,  112) -- 返回
		mSleep(interval_sleep_time)
	end
end


-------------------------------------------------
-- 点击视频栏，恢复频道栏，并分别点击四个频道
-- 每个频道浏览三篇文章
-------------------------------------------------
tap(504, 1214)
for i=1, 3 do
	moveTo(27,  190, 701,  192)
end

video_sleep_time = 200000
videos = {159,625,  96,913,  545,1139}
for i= 1, 8 do
	tap(518,  195)
	mSleep(interval_sleep_time)
	for j=1, 3 do
		tap(videos[j*2-1], videos[j*2])
		mSleep(video_sleep_time)
		moveTo(667, 1170, 662,  150)
		moveTo(667, 1170, 662,  150)
		tap(367,  248) --视频过短情况，重新播放
		mSleep(video_sleep_time)
		tap(42,  112) -- 返回
		mSleep(interval_sleep_time)
	end
end


-- 关闭wifi
--setWifiEnable(false);
--toast("关闭wifi", 3);

lockDevice(); --锁定屏幕
lua_exit();