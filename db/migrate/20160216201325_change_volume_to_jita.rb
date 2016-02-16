class ChangeVolumeToJita < ActiveRecord::Migration
  def change
    change_column :jita_margins, :mens_volume, :bigint
  end
end
