class SaleRecordsController < ApplicationController

  before_action :require_logged_in!, :log_client_activity

  def show
    @records = SaleRecord.paginate(:page => params[:page], per_page: 15).order( 'transaction_date_time DESC' )
  end

  def station_sums
    @item_sums = SaleRecord.joins(:station).group('stations.name').sum(:total_sale_profit)
    @item_sums = @item_sums.sort_by { |e| e[1] }.reverse
    @total = @item_sums.map{|e| e[1]}.reduce(:+)
  end

  def items_sums
    @item_sums = SaleRecord.joins(:eve_item).group('eve_items.name').sum(:total_sale_profit)
    @item_sums = @item_sums.sort_by { |e| e[1] }.reverse
    @total = @item_sums.map{|e| e[1]}.reduce(:+)
  end

  def stations_items_sums
    @item_sums = SaleRecord.joins(:station,:eve_item).group('stations.name','eve_items.name').sum(:total_sale_profit)
    @item_sums = @item_sums.sort_by { |e| e[1] }.reverse
    @total = @item_sums.map{|e| e[1]}.reduce(:+)
  end

end