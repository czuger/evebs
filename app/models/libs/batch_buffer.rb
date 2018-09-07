module Libs

  class BatchBuffer

    def initialize( class_name, action=:insert )
      @batch_buffer = []
      @class_name = class_name
      @action = action
    end

    def add_data( data )
      @batch_buffer << data
      flush_buffer if @batch_buffer.count > 5000
    end

    def flush_buffer
      send action
      @batch_buffer.clear
    end

    private

    def insert
      @class_name.constantize.import( @batch_buffer )
    end

    def touch
      @class_name.constantize.where( id: @data ).update_all( touched: true, updated_at: Time.now )
    end

  end

end
