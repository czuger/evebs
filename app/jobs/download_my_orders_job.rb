class DownloadMyOrdersJob < ApplicationJob

  queue_as :default

  def perform( user )
    puts "Downloading orders for #{user.name}"

    Esi::DownloadMyOrders.new.update( user )
  end

end