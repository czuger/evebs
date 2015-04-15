class ChooseItemsController < ApplicationController

  autocomplete :eve_item, :name_lowcase, full: true

  def index
    @letters = EveItem.select(:first_letter).distinct.sort
  end

  def edit
    first_letter = params[:id][0] # The 0 protect agains injection. We expect only a single letter
    @items = EveItem.where('first_letter=?',first_letter).order( :name )
    @per_group_count = (@items.length/4.0).ceil
  end

  def new
    # @eve_item = EveItem.first
  end

  def create
  end

end
