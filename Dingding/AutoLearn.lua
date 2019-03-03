require "TSLib"

math.randomseed(os.time())

function unlock_device()
	flag = deviceIsLock(); 
	if flag ~= 0 then
		unlockDevice();    
	end
end


function lock_device()
	lockDevice(); --锁定屏幕
	lua_exit();
end


function turn_on_wifi()
	setWifiEnable(true);
	toast("开启wifi", 3);
	mSleep(20000);
end


function turn_off_wifi(...)
	setWifiEnable(false);
	toast("关闭wifi", 3);
end


function open_app(interval_sleep_time)
	pressHomeKey();
	toast("返回桌面", 3);
	mSleep(interval_sleep_time)
	if multiColor({{  219, 1145, 0xd20200}}) == true then
		tap(219, 1145)
		mSleep(interval_sleep_time)
		tap(42,  112) -- 从之前浏览的内容返回
		mSleep(interval_sleep_time)
	else
		lua_exit() -- 避免点到其他东西
	end
end


function sign_in(user, passwd, interval_sleep_time)
	tap(631,  542) 
	mSleep(interval_sleep_time)
	-- user
	touchDown(241,  546);       --点击输入框获取焦点（假设输入框坐标已知）
	mSleep(30)
	touchUp(241,  546);
	mSleep(interval_sleep_time);             --延迟 1 秒以便获取焦点，注意某些应用不获取焦点无法输入
	inputText(user); --在输入框中输入字符串并回车；此函数在某些应用中无效，如支付宝、密码输入框等位置，甚至可能会导致目标应用闪退
	mSleep(interval_sleep_time)
	-- passwd
	touchDown(71,  699);       --点击输入框获取焦点（假设输入框坐标已知）
	mSleep(30)
	touchUp(71,  699);
	mSleep(interval_sleep_time);             --延迟 1 秒以便获取焦点，注意某些应用不获取焦点无法输入
	inputText(passwd); 
	mSleep(interval_sleep_time)
	tap(357,  822)
	mSleep(interval_sleep_time)
end


function sign_out(interval_sleep_time)
	open_app(interval_sleep_time)
	tap(362, 1215) -- 点击学习栏
	mSleep(interval_sleep_time)
	tap(665,   94) -- 右上角用户栏
	mSleep(interval_sleep_time)
	tap(349,  911)
	mSleep(interval_sleep_time)
	tap(357,  864)
	mSleep(interval_sleep_time)
	tap(561,  710)
	mSleep(interval_sleep_time)
end


-------------------------------------------------
-- 点击文章栏，根据概率向左滑或向右滑频道栏
-- 随机点击三个频道，每个频道浏览三篇文章
-------------------------------------------------
function read_passages(channels, passages, right_prob, interval_sleep_time, passage_sleep_time)
	tap(362, 1215)
	mSleep(interval_sleep_time)
	
	if math.random() < right_prob then
		moveTo(602,  192, 27,  190)
	else
		moveTo(27,  190, 701,  192)
	end
	mSleep(interval_sleep_time)
	
	for i= 1, 3 do
		c = math.random(1, 5)
		tap(channels[c*2-1],  channels[c*2])
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
end


-------------------------------------------------
-- 点击视频栏，根据概率向左滑或向右滑频道栏
-- 并分别点击五个频道，每个频道浏览三个视频
-------------------------------------------------
function watch_video(chnnels, videos, right_prob, interval_sleep_time, video_sleep_time)
	tap(504, 1214)
	if math.random() < right_prob then
		moveTo(602,  192, 27,  190)
	else
		moveTo(27,  190, 701,  192)
	end
	mSleep(interval_sleep_time)

	for i= 1, 4 do
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
end


interval_sleep_time = 5000  -- time between clicks
passage_sleep_time = 150000
video_sleep_time =   200000
channel_locations = {38,179,  181,189,  289,191,  421,186, 532,191}
passage_locations = {493,677,  529,921,  526,1087}
videos_locations = {159,625,  96,913,  545,1139}
right_prob = 0.6
user = "XXXXXXXX"
passwd = "XXXXXXXXX"



-- 执行流程
unlock_device()
sign_out(interval_sleep_time)
sign_in(user, passwd, interval_sleep_time)
read_passages(channel_locations, passage_locations, right_prob, interval_sleep_time, passage_sleep_time)
watch_video(channel_locations, videos_locations, right_prob, interval_sleep_time, video_sleep_time)