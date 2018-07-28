class DownloadMyAssetsJob < ApplicationJob

  queue_as :default

  def perform( user )
    puts "Downloading assets for #{user.name}"

    Esi::DownloadMyBlueprintsModifications.new.update( user )
    Esi::DownloadMyAssets.new.update( user )
  end

end