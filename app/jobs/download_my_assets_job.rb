class DownloadMyAssetsJob < ApplicationJob

  queue_as :default

  def perform( character )
    Esi::DownloadMyAssets.new.update( character )
  end

end