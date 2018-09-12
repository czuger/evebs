module Process

  class DeleteOldSalesFinals

    def self.delete

      Banner.p 'About to delete old sales finals.'

      sales_to_delete = SalesFinal.where( 'created_at < ?', Time.now - 1.month )
      puts "#{sales_to_delete.count} sales_final deleted."
      sales_to_delete.delete_all
    end
  end

end
