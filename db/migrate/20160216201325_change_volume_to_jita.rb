class ChangeVolumeToJita < ActiveRecord::Migration[4.2]
  def change
    change_column :jita_margins, :mens_volume, :bigint
  end
end
