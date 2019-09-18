module CronProcesses
	class Daily

		def self.download_data
			ActiveRecord::Base.transaction do
				Esi::DownloadHistorySetProcessCount.new.update
			end

			Esi::DownloadHistory.new.download
		end

		def self.update_data
			ActiveRecord::Base.transaction do
				Process::UpdateTradeVolumeEstimationFromDownloadedHistoryData.new.update
				Process::UpdateEveMarketHistoriesGroup.new.update

				Process::DeleteOldSalesFinals.delete

				# Be sure to compute avg prices weeks before to compute items costs.
				Sql::UpdateWeeklyPriceDetails.execute

				Process::UpdateEveItemsCosts.new.update

				Sql::UpdatePricesAdvicesDaily.execute

				Misc::LastUpdate.set( :daily )
			end
		end

	end
end