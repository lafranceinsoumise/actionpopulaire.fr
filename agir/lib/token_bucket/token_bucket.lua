-- value_key timestamp_key max_value interval now amount
--
-- interval and now must be in seconds

local value_key = KEYS[1]
local timestamp_key = KEYS[2]
local max_value = tonumber(ARGV[1])
local interval = tonumber(ARGV[2])
local now = tonumber(ARGV[3])
local amount = tonumber(ARGV[4])

local current_value
local expiry_time
local previous_value = redis.call('GET', value_key)
local last_update = redis.call('GET', timestamp_key)

if (previous_value == false) or (last_update == false) then
    -- if we found no record, we set current_value to initial_value
    -- and last_update to now
    current_value = max_value
else
    current_value = previous_value + (now - last_update) / interval

    if current_value > max_value then
        current_value = max_value
    end
end

if amount > current_value then
    return false
else
    current_value = current_value - amount
    expiry_time = math.ceil((max_value - current_value) * interval)
    redis.call('SET', value_key, current_value, 'EX', expiry_time)
    redis.call('SET', timestamp_key, now, 'EX', expiry_time)
    return true
end
