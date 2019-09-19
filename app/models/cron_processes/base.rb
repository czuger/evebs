module CronProcesses
	class Base

		def initialize
			@download_disabled = (ENV['EBS_DOWNLOAD_DISABLED'] == 'true')
		end

	end
end