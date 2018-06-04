class AddMensVolumeToJitaMargin < ActiveRecord::Migration[4.2]
  def change
    add_column :jita_margins, :mens_volume, :integer, null: false, default: 0
  end
end
