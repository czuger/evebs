namespace :process do

  desc 'Update sold volumes from history in EveMarketVolume'
  task :update_volumes_from_history => :environment do
    Esi::DownloadHistory.new(debug_request: false ).update
  end

end