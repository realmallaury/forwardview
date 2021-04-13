import pandas as pd


def macd(DF, fast_window, slow_window, signal_window):
    """Calculate MACD (typical values a = 12; b =26, c =9)"""
    df, temp = DF.copy(), pd.DataFrame()
    temp["MA_Fast"] = (
        df["close"].rolling(window=fast_window, min_periods=fast_window).mean()
    )
    temp["MA_Slow"] = (
        df["close"].rolling(window=slow_window, min_periods=slow_window).mean()
    )

    df["MACD"] = temp["MA_Fast"] - temp["MA_Slow"]
    df["MACD_SIGNAL"] = (
        df["MACD"].ewm(span=signal_window, min_periods=signal_window).mean()
    )
    df.dropna(inplace=True)

    return df


def atr(DF, window):
    """Calculate True Range and Average True Range."""
    df, temp = DF.copy(), pd.DataFrame()
    temp["H-L"] = abs(df["high"] - df["low"])
    temp["H-PC"] = abs(df["high"] - df["close"].shift(1))
    temp["L-PC"] = abs(df["low"] - df["close"].shift(1))

    temp["TR"] = temp[["H-L", "H-PC", "L-PC"]].max(axis=1, skipna=False)
    df["ATR"] = temp["TR"].ewm(span=window, min_periods=window, adjust=False).mean()

    return df


def keltner_channel(DF, window):
    """Keltner Channels are a trend following indicator used to identify reversals with channel breakouts and
    channel direction. Channels can also be used to identify overbought and oversold levels when the trend
    is flat.
    """
    df = DF.copy()
    temp = atr(df, window=window)

    df["KELTNER_MBAND"] = (
        df["close"].ewm(span=window, min_periods=window, adjust=False).mean()
    )
    df["KELTNER_HBAND"] = df["KELTNER_MBAND"] + (2.25 * temp["ATR"])
    df["KELTNER_LBAND"] = df["KELTNER_MBAND"] - (2.25 * temp["ATR"])
    df.dropna(inplace=True)

    return df
