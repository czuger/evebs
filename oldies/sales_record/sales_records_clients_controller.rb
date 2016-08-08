class SalesRecordsClientsController < ApplicationController

  before_action :require_logged_in!, :log_client_activity

  def show
    @item_sums = SaleRecord.where('eve_clients.id=?',params[:id]).joins(:eve_client,:eve_item,:station).pluck(
      'eve_items.name', 'stations.name', :total_sale_profit, :transaction_date_time)
    @item_sums = @item_sums.sort_by { |e| e[3] }.reverse
    @total = @item_sums.map{|e| e[2]}.reduce(:+)

  end

  def index
    @item_sums = SaleRecord.joins(:eve_client).group('eve_clients.name','eve_clients.id').sum(:total_sale_profit)
    @item_sums = @item_sums.sort_by { |e| e[1] }.reverse
    @total = @item_sums.map{|e| e[1]}.reduce(:+)
  end

end
