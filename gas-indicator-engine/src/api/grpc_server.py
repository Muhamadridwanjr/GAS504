import grpc
from concurrent import futures
from loguru import logger

# Import proto-generated classes
from src.models.protobuf import indicator_pb2
from src.models.protobuf import indicator_pb2_grpc
from src.lib.config import settings

class IndicatorServiceServicer(indicator_pb2_grpc.IndicatorServiceServicer):
    def Calculate(self, request, context):
        logger.info(f"gRPC Calculate req: {request.symbol} {request.timeframe}")
        
        # Format grpc request into dict list
        ohlc_data = []
        for o in request.ohlc:
            ohlc_data.append({
                "time": o.time,
                "open": o.open,
                "high": o.high,
                "low": o.low,
                "close": o.close,
                "volume": o.volume
            })
            
        if not ohlc_data:
            from src.data.redis_provider import RedisProvider
            from src.lib.config import settings
            redis_provider = RedisProvider(settings.REDIS_HOST, settings.REDIS_PORT, settings.REDIS_PASSWORD)
            ohlc_data = redis_provider.get_ohlc(request.symbol, request.timeframe)
            
        from src.indicators import calculate_all
        
        # indicators_req is a list of IndicatorRequest, which has .name, .periods, .params
        # calculate_all expects objects with these attributes, which grpc generated classes have
        calc_results = calculate_all(ohlc_data, request.indicators)
        
        response = indicator_pb2.CalculateResponse()
        for res in calc_results:
            result = indicator_pb2.IndicatorResult(
                name=res["name"],
                period=res["period"],
                values=res["values"],
                timestamps=res["timestamps"]
            )
            response.results.append(result)
            
        return response

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    indicator_pb2_grpc.add_IndicatorServiceServicer_to_server(IndicatorServiceServicer(), server)
    server.add_insecure_port(f'[::]:{settings.GRPC_PORT}')
    logger.info(f"gRPC server started on port {settings.GRPC_PORT}")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
