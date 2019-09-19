module CronProcesses
	class Daily < Base

		def run
			Misc::Banner.p( 'Daily process started', true )

			chrono = Misc::Chrono.new

			download_data unless @download_disabled
			update_data

			chrono.p
			Misc::Banner.p( 'Daily process finished', true )
		end

		private

		def download_data
			ActiveRecord::Base.transaction do
				Esi::DownloadHistorySetProcessCount.new.update
			end

			Esi::DownloadHistory.new.download
		end

		def update_data
			ActiveRecord::Base.transaction do
				Process::UpdateEveMarketHistoriesGroup.new.update
				Sql::UpdateTradeVolumeEstimationFromDownloadedHistoryData.execute
				# Process::UpdateTradeVolumeEstimationFromDownloadedHistoryData.new.update

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