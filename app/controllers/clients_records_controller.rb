class ClientsRecordsController < ApplicationController
  def show
    @item_sums = SaleRecord.where('eve_clients.id=?',params[:id]).joins(:eve_client,:eve_item).group('eve_items.name').sum(:total_sale_profit)
    @item_sums = @item_sums.sort_by { |e| e[1] }.reverse
    @total = @item_sums.map{|e| e[1]}.reduce(:+)
  end

  def index
    @item_sums = SaleRecord.joins(:eve_client).group('eve_clients.name','eve_clients.id').sum(:total_sale_profit)
    @item_sums = @item_sums.sort_by { |e| e[1] }.reverse
    @total = @item_sums.map{|e| e[1]}.reduce(:+)
  end
end
