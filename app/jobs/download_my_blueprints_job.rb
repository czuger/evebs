class DownloadMyBlueprintsJob < ApplicationJob

  queue_as :default

  def perform( user )
    puts "Downloading blueprints for #{user.name}"

    Esi::DownloadMyBlueprintsModifications.new.update( user )
  end

end